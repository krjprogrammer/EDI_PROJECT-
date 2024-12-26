import {
  Flex,
  Icon,
  Spinner,
  Table,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import React from "react";
import axios from "axios";
import { FaDownload } from "react-icons/fa";
import { IoIosCloudDone } from "react-icons/io";
import { TbAlertOctagonFilled } from "react-icons/tb";

const FilesTable = ({
  data,
  csvLoadingMap,
  excelLoadingMap,
  formatDateTime,
  handleDownload,
  handleExcelDownload,
  handleInputDownload,
}) => {
  const handleEdiExcelFileDownload = async (id, date) => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/edi/download_edi_excel",
        { id, date }
      );
      console.log("EDI Excel file downloaded:", response.data);
    } catch (error) {
      console.error("Error downloading EDI Excel file:", error);
    }
  };

  const handleEDIExcelDownload = async (fileId, status, fileName, date) => {
    if (!status) {
      toast({
        title: "EDI Excel File not generated",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    fileName = fileName.split(".")[0];
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/edi/download_edi_excel/",
        { id: fileId, date: date },
        {
          responseType: "blob",
        }
      );

      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      saveAs(blob, `date_with_validations.xlsx`);

      toast({
        title: "EDI Excel Download Successful",
        description: "The file has been downloaded.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "EDI Excel Download Failed",
        description:
          error.response?.data ||
          "An error occurred while downloading the file.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Table variant="simple">
      <Thead>
        <Tr bg={"blue.400"}>
          <Th color={"white"}>File Name</Th>
          <Th color={"white"}>Type</Th>
          <Th color={"white"}>Date</Th>
          <Th color={"white"}>CSV</Th>
          <Th color={"white"}>Excel</Th>
          <Th color={"white"}>EDI Excel</Th>
          <Th color={"white"}>EDI</Th>
          <Th color={"white"}>Created at</Th>
          <Th color={"white"}>Created By</Th>
          <Th color={"white"}>Status</Th>
        </Tr>
      </Thead>
      <Tbody>
        {data.length > 0 ? (
          data.reverse().map((item) => (
            <Tr key={item.id}>
              <Td>{item.file_name}</Td>
              <Td>{item.file_type}</Td>
              <Td>{item.file_date}</Td>
              <Td
                cursor={"pointer"}
                onClick={() =>
                  handleDownload(item.id, item.upload_status, item.file_name)
                }
              >
                <Flex justify="center" align="center">
                  {csvLoadingMap[item.id] ? (
                    <Spinner />
                  ) : (
                    <FaDownload color="blue" />
                  )}
                </Flex>
              </Td>
              <Td
                cursor={"pointer"}
                onClick={() =>
                  handleExcelDownload(
                    item.id,
                    item.upload_status,
                    item.file_name
                  )
                }
              >
                <Flex justify="center" align="center">
                  {excelLoadingMap[item.id] ? (
                    <Spinner />
                  ) : (
                    <FaDownload color="red" />
                  )}
                </Flex>
              </Td>

              <Td
                cursor={"pointer"}
                onClick={() =>
                  handleEDIExcelDownload(
                    item.id,
                    item.upload_status,
                    item.file_name,
                    item.file_date
                  )
                }
              >
                <Flex justify="center" align="center">
                  <FaDownload color="purple" />
                </Flex>
              </Td>
              <Td
                cursor={"pointer"}
                onClick={() =>
                  handleInputDownload(
                    item.id,
                    item.upload_status,
                    item.file_name
                  )
                }
              >
                <Flex justify="center" align="center">
                  <FaDownload color="green" />
                </Flex>
              </Td>
              <Td>{formatDateTime(item.created_at)}</Td>
              <Td>{item.created_by}</Td>
              <Td>
                <Flex justify="center" align="center">
                  {item.upload_status ? (
                    <Icon as={IoIosCloudDone} color="green" fontSize={"20px"} />
                  ) : (
                    <Icon
                      as={TbAlertOctagonFilled}
                      color="red"
                      fontSize={"20px"}
                    />
                  )}
                </Flex>
              </Td>
            </Tr>
          ))
        ) : (
          <Tr>
            <Td colSpan="13" textAlign="center">
              Data not available
            </Td>
          </Tr>
        )}
      </Tbody>
    </Table>
  );
};

export default FilesTable;
