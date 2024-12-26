from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import files,Archive,User,Dependent,Employee,EDI_USER_DATA
import json
from io import BytesIO
import pyodbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .processinputfile import parse_edi_to_csv, send_success_email, send_error_email,parse_custodial_data
from rest_framework.parsers import MultiPartParser, FormParser
import shutil, os, re
from datetime import datetime
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .serializers import FilesSerializer,SignupSerializer, LoginSerializer,ArchiveSerializer,OTPLoginSerializer
import pandas as pd
import tempfile
from django.core.files.storage import FileSystemStorage
import mimetypes
from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.timezone import timedelta
from django.utils.timezone import now
from .checks import perform_checks

class SignupView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully', 'user': {'username': user.username, 'email': user.email}}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                return Response({'message': 'Login successful', 'username': user.username}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def download_file(request):
    if request.method == 'POST':
        try:
          
            data = json.loads(request.body)
            file_id = data.get("id")
            if not file_id:
                return HttpResponse("File ID not provided", status=400)

            
            file_record = get_object_or_404(files, id=file_id)

      
            if not file_record.file_path:
                return HttpResponse("File path not set for the record.", status=404)

            file_path = file_record.file_path.path  

          
            if os.path.isfile(file_path):
                pass
            else:
                file_path = file_path.replace("\\media\\media\\", "\\media\\", 1)
                
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found at path: {file_path}")

            
            file_name = file_record.file_name
            if not file_name.endswith('.csv'):
                file_name += '.csv'

            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response

        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON format in the request body.", status=400)
        except FileNotFoundError as e:
            return HttpResponse(str(e), status=404)
        except Exception as e:
            return HttpResponse(f"An unexpected error occurred: {str(e)}", status=500)
    else:
        return HttpResponse("Method not allowed. Please use POST.", status=405)

@csrf_exempt
def download_excel_file(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            file_id = data.get("id")
            if not file_id:
                return HttpResponse("File ID not provided", status=400)

            file_record = get_object_or_404(files, id=file_id)
            if not file_record.file_path:
                raise Http404("File not found")

            file_path = file_record.file_path.path
            print("aaaa",file_path)
            try:
                try:
                    df = pd.read_csv(file_path)
                except:
                    corrected_file_path = file_path.replace("\\media\\media\\", "\\media\\", 1)
                    print(corrected_file_path,"jjjhhjj")
                    df = pd.read_csv(corrected_file_path)
            except FileNotFoundError:
                raise Http404("CSV file not found on the server.")

            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
                temp_excel_path = tmp_file.name
                df.to_excel(temp_excel_path, index=False, engine="openpyxl")

            with open(temp_excel_path, 'rb') as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{file_record.file_name}.xlsx"'
            

            os.remove(temp_excel_path)

            return response

        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON", status=400)

    return HttpResponse("Method not allowed", status=405)

def download_input_file(request, file_id):
    file_instance = get_object_or_404(files, id=file_id)
    
    file_path = file_instance.input_file_path.path
    print(file_path)
    if not file_path.startswith(settings.MEDIA_ROOT):
        raise Http404("File path is invalid or not within the MEDIA_ROOT")

    if not os.path.exists(file_path):
        raise Http404("File does not exist")

    file_name = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)

    response = HttpResponse(open(file_path, 'rb'), content_type=mime_type)
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


class FilesListView(generics.ListAPIView):
    queryset = files.objects.all()
    serializer_class = FilesSerializer

class FilesFilterView(APIView):
    def get(self, request):
        file_type = request.query_params.get('file_type')
        file_date = request.query_params.get('file_date')
        print(file_date,file_type)

        if file_type is None or file_date is None:
            return Response(
                {"error": "Both file_type and file_date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        files_filtered = files.objects.filter(file_type=file_type, file_date=file_date)
        print(files_filtered)

        serializer = FilesSerializer(files_filtered, many=True)
        return Response(serializer.data)
    

class ArchiveListView(generics.ListAPIView):
    queryset = Archive.objects.all()
    serializer_class = ArchiveSerializer    

class ArchiveFilterView(APIView):
    def get(self, request):

        file_type = request.query_params.get('file_type')
        file_date = request.query_params.get('file_date')
        print(file_date,file_type)


        if file_type is None or file_date is None:
            return Response(
                {"error": "Both file_type and file_date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        files_filtered = Archive.objects.filter(file_type=file_type, file_date=file_date)
        print(files_filtered)
        serializer = ArchiveSerializer(files_filtered, many=True)
        return Response(serializer.data)
    
    
output_folder = r"C:\Users\avina\OneDrive\Desktop\Output"
system_folder = r"C:\Users\avina\OneDrive\Desktop\edi-backend\edi\media\csv_files"
archive_folder = r"C:\Users\avina\OneDrive\Desktop\Archive"
from dateutil import parser
class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        file = request.FILES.get('file')
        email = request.data.get('email', 'avinashkalmegh93@gmail.com')

        if not file:
            return Response({"message": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file_name = file.name
        storage = FileSystemStorage(location='media/input_files/')
        saved_file_name = storage.save(file.name, file)
        saved_file_path = storage.path(saved_file_name)

        if True:
            match = re.match(r"^EDI_(\d{3})_(\d{2}-\d{2}-\d{4})$", os.path.splitext(file_name)[0])
            if not match:
                pass
                # return Response({"message": "Invalid file name format. Expected format: EDI_XXX_MM-DD-YYYY"}, 
                #                 status=status.HTTP_400_BAD_REQUEST)

            file_type = ""
            file_date_str = ""
            file_date = 23-11-2024

            output_folder = "media/csv_files/"
            J=output_folder
            archive_folder = "media/archive/"
            os.makedirs(output_folder, exist_ok=True)
            os.makedirs(archive_folder, exist_ok=True)

            input_file_path = os.path.join(output_folder, file_name)
            with open(input_file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            output_file_path = parse_edi_to_csv(input_file_path, output_folder,J)
            insert_df = pd.read_csv(output_file_path)
            filtered_df = insert_df[insert_df['SUB/DEP'] != 'Subscriber']
            if "ADDRESS 2" not in filtered_df.columns:
                filtered_df['ADDRESS 2'] = ''
            updated_insert_df = filtered_df[["FIRST NAME","SSN","SEX","DOB","ADDRESS 1","ADDRESS 2","CITY","STATE","ZIP"]]
            subscribers = []
            def convert_to_date_components(date_string):
                try:
                    parsed_date = parser.parse(date_string)
                    formatted_date = parsed_date.strftime("%Y-%m-%d")
                    return {
                        "formatted_date": formatted_date,
                        "year": parsed_date.year,
                        "month": parsed_date.month,
                        "day": parsed_date.day,
                    }
                except (parser.ParserError, TypeError, ValueError):
                    return None
            for index, row in updated_insert_df.iterrows():
                date = row['DOB']
                obj = convert_to_date_components(date)
                year = obj['year']
                month = obj['month']
                day = obj['day']
                subscriber = Dependent(DPDOBY=year, DPDOBM=month,DPDOBD=day,DPSEX=row['SEX'],DPSSN=row['SSN'])
                subscribers.append(subscriber)
            Dependent.objects.bulk_create(subscribers)
            new_filtered_df = insert_df[insert_df['SUB/DEP'] == 'Subscriber']
            if "ADDRESS 2" not in new_filtered_df.columns:
                new_filtered_df['ADDRESS 2'] = ''
            new_updated_insert_df = new_filtered_df[["FIRST NAME","SSN","SEX","DOB","ADDRESS 1","ADDRESS 2","CITY","STATE","ZIP"]]
            new_subscribers = []
            for index, row in new_updated_insert_df.iterrows():
                date = row['DOB']
                obj = convert_to_date_components(date)
                year = obj['year']
                month = obj['month']
                day = obj['day']
                subscriber = Employee(EMDOBY=year, EMDOBM=month,EMDOBD=day,EMSEX=row['SEX'],EMSSN=row['SSN'],EMCITY=row['CITY'],EMST=row['STATE'],EMZIP5=row['ZIP'],EMADR1=row['ADDRESS 1'],EMADR2=row["ADDRESS 2"])
                new_subscribers.append(subscriber)
            Employee.objects.bulk_create(new_subscribers)
            shutil.move(input_file_path, os.path.join(archive_folder, file_name))
            pth = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.csv")
            print(pth)
            file_record = files.objects.create(
                file_name=file_name,
                file_type=file_type,
                file_date=file_date,
                file_path=pth,
                created_by="API",
                upload_status=True,
                email_sent_status=True,
                email_sent_to=email,
                input_file_path=saved_file_path
            )

            # send_success_email(email, file_name, output_file_path)
            return Response({"message": "File processed successfully"}, status=status.HTTP_200_OK)

        # except Exception as e:
        #     send_error_email(email, file_name, str(e))
        #     return Response({"message": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        


smtp_config = {
    'host': 'mail.privateemail.com',
    'port': 465,
    'user': 'support@disruptionsim.com',
    'password': 'Onesmarter@2023'
}

   
def send_mail(email,otp):
    
    try:
        server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
        server.login(smtp_config['user'], smtp_config['password'])

        msg = MIMEMultipart()
        msg['From'] = smtp_config['user']
        msg['To'] = email
        msg['Subject'] = 'Your OSI Pay OTP for Secure Login'

       
        body = f"""
        <p>Dear User,</p>
        <p>Thank you for using OSI Pay. For added security, we have implemented a two-factor authentication process. Please use the following One-Time Password (OTP) to complete your login:</p>
        <p>Your OTP: {otp}</p>
        <p>This OTP is valid for the next 10 minutes. If you did not request this, please disregard this email.</p>
        <p>Thank you for choosing OSI Pay.</p>
        <p></p>
        <p></p>
        <p>Best regards,</p>
        <p>The OSI Pay Team</p>
        """

        msg.attach(MIMEText(body, 'html'))
        # Include the main recipient and the CC in the recipients list
        recipients = email
        server.send_message(msg, from_addr=smtp_config['user'], to_addrs=recipients)
        server.quit()
        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user with email and password
        user = authenticate(username=email, password=password)
        if not user:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate OTP and send email
        otp = user.generate_otp()
        send_mail(
           email,
           otp
        )
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        
        
        
class OTPLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            try:
                user = User.objects.get(email=email, otp=otp)
                # Check if OTP is expired (valid for 5 minutes)
                if now() - user.last_otp_sent > timedelta(minutes=5):
                    return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

                # Successful login
                user.otp = None  # Clear OTP after use
                user.save()
                return Response({"message": "Login successful", "username": user.username}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Invalid OTP or email"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        


class Download_excel(APIView):
  def get(self, request, *args, **kwargs):
    date = request.query_params.get('date')
    connection = pyodbc.connect(
      'DRIVER={SQL Server};SERVER=PROGRAMMER\\SQLEXPRESS;DATABASE=EDI834Database;Trusted_Connection=yes;'
    )
    cursor = connection.cursor()
    query = "SELECT * FROM edi834detailedtable WHERE Date_edi = ?"
    cursor.execute(query, (date,))
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    cursor.close()
    connection.close()

    validations = perform_checks(df)
    validations_df = pd.DataFrame(validations, columns=['Validation Errors'])

    output_folder = 'media/output_excels/' 
    os.makedirs(output_folder, exist_ok=True)

    workbook_path = os.path.join(output_folder, f'data_with_validations_{date}.xlsx')
    with pd.ExcelWriter(workbook_path, engine='xlsxwriter') as writer:
      df.to_excel(writer, index=False, sheet_name='DataFrame')
      validations_df.to_excel(writer, index=False, sheet_name='Validations')

    with open(workbook_path, 'rb') as excel_file:
      response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      response['Content-Disposition'] = f'attachment; filename="{os.path.basename(workbook_path)}"' 
      return response
    

class Download_edi_Custodial_xlsx(APIView):
    def get(self, request):
        date = request.query_params.get('date')
        if not date:
            return HttpResponse("Date parameter is missing", status=400)

        output_folder = "media/csv_files/"
        os.makedirs(output_folder, exist_ok=True)

        filtered_data = EDI_USER_DATA.objects.filter(date_edi=date)
        if not filtered_data.exists():
            return HttpResponse("No data found for the given date", status=404)

        db_df = pd.DataFrame.from_records(filtered_data.values())
        db_df.drop(columns=['temp_ssn'],inplace=True)
        
        excel_filename = os.path.join(output_folder, f"edi_data_{date}.xlsx")
        db_df.to_excel(excel_filename, index=False)
        with open(excel_filename, 'rb') as excel_file:
            response = HttpResponse(excel_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=custodial_data_{date}.xlsx'
        return response
    
class Download_edi_Custodial_csv(APIView):
    def get(self, request):
        date = request.query_params.get('date')
        if not date:
            return HttpResponse("Date parameter is missing", status=400)

        output_folder = "media/csv_files/"
        os.makedirs(output_folder, exist_ok=True)

        filtered_data = EDI_USER_DATA.objects.filter(date_edi=date)
        if not filtered_data.exists():
            return HttpResponse("No data found for the given date", status=404)

        db_df = pd.DataFrame.from_records(filtered_data.values())
        db_df.drop(columns=['temp_ssn'],inplace=True)
        csv_data = db_df.to_dict(orient='records')
        cus_df = parse_custodial_data(csv_data)
        excel_filename = os.path.join(output_folder, f"edi_data_{date}.csv")
        cus_df.to_excel(excel_filename, index=False)
        with open(excel_filename, 'rb') as excel_file:
            response = HttpResponse(excel_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=custodial_data_{date}.csv'
        return response
