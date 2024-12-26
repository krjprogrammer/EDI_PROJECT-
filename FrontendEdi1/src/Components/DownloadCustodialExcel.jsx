import React, { useState } from "react";
import {
  Box,
  Button,
  Flex,
  Input,
  Text,
  useToast,
  Icon,
} from "@chakra-ui/react";
import { FiUpload } from "react-icons/fi";
import axios from "axios";

const DownloadCustodialExcel = () => {
  const [file, setFile] = useState(null);
  const [csvFileUrl, setCsvFileUrl] = useState(null);
  const toast = useToast();

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select a file to upload.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/edi/upload_custodial_excel_data",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      toast({
        title: "File uploaded successfully",
        description: response.data.message || "The file has been uploaded.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      setCsvFileUrl(response.data.csv_file_url);
      setFile(null);
    } catch (error) {
      toast({
        title: "Upload failed",
        description: error.response?.data?.message || "Something went wrong.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleDownload = () => {
    if (csvFileUrl) {
      const link = document.createElement("a");
      link.href = csvFileUrl;
      link.download = csvFileUrl.split("/").pop();
      link.click();
    }
  };

  return (
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
      <Text fontSize="lg" fontWeight="bold" color="teal.700">
        Upload Custodial EDI File
      </Text>

      <Flex
        direction="row"
        justifyContent={"space-between"}
        alignItems="center"
        gap={4}
      >
        <Button
          as="label"
          htmlFor="custodial-file-input"
          bg="blue.500"
          color="white"
          fontSize="14px"
          cursor="pointer"
          _hover={{ bg: "blue.600" }}
        >
          Choose File
          <Input
            type="file"
            id="custodial-file-input"
            onChange={handleFileChange}
            borderColor="teal.500"
            display="none"
          />
        </Button>

        {file && (
          <Text fontSize="14px" color="gray.600" textAlign="center">
            {file.name}
          </Text>
        )}

        <Button
          leftIcon={<Icon as={FiUpload} />}
          colorScheme="gray"
          onClick={handleUpload}
          isDisabled={!file}
        >
          Upload
        </Button>
      </Flex>

      {csvFileUrl && (
        <Box mt={4}>
          <Button colorScheme="teal" onClick={handleDownload}>
            Download Converted CSV File
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default DownloadCustodialExcel;
