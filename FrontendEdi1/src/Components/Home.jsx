import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  Flex,
  Input,
  FormControl,
  FormLabel,
  useToast,
  Select,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Icon,
  Spinner,
} from "@chakra-ui/react";
import { FaDownload } from "react-icons/fa";
import { IoIosCloudDone } from "react-icons/io";
import { TbAlertOctagonFilled } from "react-icons/tb";
import { saveAs } from "file-saver";
import axios from "axios";
import FilesTable from "./FilesTable";
import DownloadCustodialExcel from "./DownloadCustodialExcel";
import { FiUpload } from "react-icons/fi";

function Home() {
  const [file1, setFile1] = useState(null);
  const [date2, setDate2] = useState("");
  const [fileType, setFileType] = useState("");
  const [data, setData] = useState([]);
  const toast = useToast();
  const [uploadLoading, setUploadLoading] = useState(false);
  const [filterLoading, setFilterLoading] = useState(false);
  const [excelLoadingMap, setExcelLoadingMap] = useState({});
  const [csvLoadingMap, setCsvLoadingMap] = useState({});

  const resetFilter = () => {
    setDate2("");
    setFileType("");
    getFiles();
  };

  const handleUpload = async () => {
    if (file1) {
      let formData = new FormData();
      formData.append("file", file1);
      formData.append("email", "avinashkalmegh93@gmail.com");
      try {
        setUploadLoading(true);
        let response = await axios.post(
          "http://127.0.0.1:8000/edi/upload-file/",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log(response);
        if (response.status == 200) {
          setTimeout(() => {
            setUploadLoading(false);
            toast({
              title: "File Uploaded Successfully",
              description: "File uploaded successfully.",
              status: "success",
              duration: 3000,
              isClosable: true,
            });
            getFiles();
          }, 2000);
        }
      } catch (error) {
        console.log(error);
      }
    } else {
      toast({
        title: "Missing Information",
        description: "Please select a file and date before uploading.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const getFiles = async () => {
    try {
      let response = await axios.get("http://127.0.0.1:8000/edi/files/");
      console.log(response);
      setData(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  function formatDateTime(dateString) {
    const date = new Date(dateString);
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const year = date.getFullYear();
    const formattedDate = `${month}-${day}-${year}`;

    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    const formattedTime = `${hours}:${minutes} ${ampm}`;

    return `${formattedDate} ${formattedTime}`;
  }

  const handleDownload = async (fileId, status, fileName) => {
    if (!status) {
      toast({
        title: "CSV file not generated",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setCsvLoadingMap((prev) => ({ ...prev, [fileId]: true }));
    fileName = fileName.split(".")[0];
    try {
      // Make the API request to download the file
      const response = await axios.post(
        "http://127.0.0.1:8000/edi/download-file/",
        { id: fileId },
        {
          responseType: "blob", // Specify blob response type
        }
      );

      // Create a Blob URL for the downloaded file
      const blob = new Blob([response.data], {
        type: response.headers["content-type"],
      });
      const downloadUrl = window.URL.createObjectURL(blob);

      // Create a link element, set download attributes, and trigger a click
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download =
        response.headers["content-disposition"]
          ?.split("filename=")[1]
          ?.replace(/"/g, "") || `${fileName}`;
      document.body.appendChild(link);
      link.click();

      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      // Show success toast
      toast({
        title: "Download Successful",
        description: "The file has been downloaded.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      setCsvLoadingMap((prev) => ({ ...prev, [fileId]: false }));
    } catch (error) {
      // Show error toast
      setCsvLoadingMap((prev) => ({ ...prev, [fileId]: false }));
      toast({
        title: "Download Failed",
        description:
          error.response?.data ||
          "An error occurred while downloading the file.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleInputDownload = async (fileId, status, fileName) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/edi/download-input-file/${fileId}/`,
        {
          responseType: "blob", // Required for file downloads
        }
      );

      // Extract file name and ensure extension is correct
      const contentDisposition = response.headers["content-disposition"];
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
        if (fileNameMatch) {
          fileName = fileNameMatch[1];
        }
      }

      // Create a URL for the file blob and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();

      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading the file", error);
    }
  };

  const handleExcelDownload = async (fileId, status, fileName) => {
    if (!status) {
      toast({
        title: "Excel File not generated",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setExcelLoadingMap((prev) => ({ ...prev, [fileId]: true }));
    fileName = fileName.split(".")[0];
    console.log("aaa", fileName);
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/edi/download-excel-file/",
        { id: fileId },
        {
          responseType: "blob",
        }
      );

      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      saveAs(blob, `${fileName}.xlsx`);

      toast({
        title: "Download Successful",
        description: "The file has been downloaded.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description:
          error.response?.data ||
          "An error occurred while downloading the file.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setExcelLoadingMap((prev) => ({ ...prev, [fileId]: false }));
    }
  };

  const handleFileFilter = async () => {
    if (!date2 || !fileType) {
      toast({
        title: "Missing Information",
        description: "Please select a date and file type before filtering.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    const [year, month, day] = date2.split("-");
    const formattedDate = `${month}-${day}-${year}`;
    setFilterLoading(true);
    try {
      let response = await axios.get(
        "http://127.0.0.1:8000/edi/files_filter/",
        {
          params: {
            file_date: formattedDate,
            file_type: fileType,
          },
        }
      );
      if (response.data.length > 0) {
        setData(response.data);
        setFilterLoading(false);
      }
    } catch (error) {
      setFilterLoading(false);
      toast({
        title: "Error Fetching Data",
        description:
          error.response?.data ||
          "An error occurred while fetching the filtered data.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  useEffect(() => {
    getFiles();
  }, []);

  return (
    <Flex
      height="100vh"
      justifyContent="center"
      bg="gray.50"
      mt={45}
      fontFamily={"rajdhani"}
    >
      <Box width="100%">
        <Flex direction="column" alignItems="flex-start" p={5}>
          <Text fontSize="25px" fontWeight="bold" my={2}>
            Upload File
          </Text>
          <Box
            width="100%"
            p={1}
            borderWidth={1}
            borderRadius="lg"
            boxShadow="md"
            bg="blue.100"
            h="auto"
          >
            <Flex
              justifyContent={"space-between"}
              alignItems={"center"}
              gap={10}
            >
              <Box
                bg="white"
                p={2}
                rounded="lg"
                shadow="md"
                maxWidth="400px"
                width="100%"
                bgGradient="linear(to-r, teal.300, blue.600)"
                textAlign="center"
              >
                <FormControl>
                  <FormLabel fontSize="lg" fontWeight="bold" color="teal.700">
                    Upload File<span style={{ color: "red" }}>*</span>
                  </FormLabel>
                  <Box
                    display="flex"
                    rounded={"md"}
                    alignItems="center"
                    justifyContent={"space-between"}
                    gap={2}
                  >
                    <Button
                      as="label"
                      htmlFor="file-input"
                      bg="blue.500"
                      color="white"
                      fontSize="14px"
                      cursor="pointer"
                      _hover={{ bg: "blue.600" }}
                    >
                      Choose File
                      <Input
                        id="file-input"
                        type="file"
                        display="none"
                        onChange={(e) => setFile1(e.target.files[0])}
                      />
                    </Button>
                    {file1 && (
                      <Text fontSize="14px" color="gray.600">
                        {file1.name}
                      </Text>
                    )}
                    <Button
                      leftIcon={<Icon as={FiUpload} />}
                      colorScheme="gray"
                      isLoading={uploadLoading}
                      onClick={handleUpload}
                      isDisabled={!file1}
                    >
                      Upload
                    </Button>
                  </Box>
                </FormControl>{" "}
              </Box>
              <Box>
                {/* <DownloadCustodialExcel /> */}
              </Box>
            </Flex>
          </Box>
          <Box
            width="100%"
            maxWidth="600px"
            p={1}
            borderWidth={1}
            borderRadius="lg"
            boxShadow="md"
            bg="white"
            mt={4}
          >
            <Flex gap={4}>
              <FormControl>
                <FormLabel fontSize="13px">
                  File Type<span style={{ color: "red" }}>*</span>
                </FormLabel>
                <Select
                  h={8}
                  fontSize="13px"
                  value={fileType}
                  onChange={(e) => setFileType(e.target.value)}
                >
                  <option>Select</option>
                  <option value="834">834</option>
                  <option value="835">835</option>
                </Select>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="13px">
                  Date<span style={{ color: "red" }}>*</span>
                </FormLabel>
                <Input
                  h={8}
                  fontSize="13px"
                  type="date"
                  value={date2}
                  onChange={(e) => setDate2(e.target.value)}
                />
              </FormControl>
              <Button
                colorScheme="blue"
                w="130px"
                mt="27px"
                fontSize="13px"
                size="sm"
                onClick={handleFileFilter}
                isLoading={filterLoading}
              >
                Filter
              </Button>
              <Button
                colorScheme="blue"
                w="130px"
                mt="27px"
                fontSize="13px"
                size="sm"
                onClick={resetFilter}
              >
                Reset
              </Button>
            </Flex>
          </Box>
          <Box mt={6} width="100%">
            <FilesTable
              data={data}
              csvLoadingMap={csvLoadingMap}
              excelLoadingMap={excelLoadingMap}
              formatDateTime={formatDateTime}
              handleDownload={handleDownload}
              handleInputDownload={handleInputDownload}
              handleExcelDownload={handleExcelDownload}
            />
          </Box>
        </Flex>
      </Box>
    </Flex>
  );
}

export default Home;
