import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Heading,
  Input,
  Select,
  Table,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from '@chakra-ui/react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from 'chart.js';
import axios from 'axios';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, Title);

const Dashboard = () => {
  const [ediFiles, setEdiFiles] = useState([]);
  const [typeFilter, setTypeFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  // Fetch files from the API
  const getFiles = async () => {
    try {
      let response = await axios.get("http://127.0.0.1:8000/edi/files/");
      setEdiFiles(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  // Function to handle filtering
  const handleFilter = () => {
    const filteredData = ediFilesData.filter((file) => {
      const matchesType = typeFilter ? file.fileType === typeFilter : true;
      const matchesDate = dateFilter ? file.fileDate === dateFilter : true;
      return matchesType && matchesDate;
    });
    setEdiFiles(filteredData);
  };

  // Reset filters
  const resetFilters = () => {
    setTypeFilter('');
    setDateFilter('');
getFiles();  };

  // Filter the files based on their status
  const processedFiles = ediFiles.filter((file) => file.upload_status === true);
  const failedFiles = ediFiles.filter((file) => file.upload_status === false);

  // Calculate counts for processed and failed files
  const processedCount = processedFiles.length;
  const failedCount = failedFiles.length;

  // Pie chart data
  const pieChartData = {
    labels: ['Processed', 'Failed'],
    datasets: [
      {
        data: [processedCount, failedCount],
        backgroundColor: ['#4caf50', '#f44336'], // Green for processed, Red for failed
      },
    ],
  };

  // Pie chart options
  const pieChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function (tooltipItem) {
            return `${tooltipItem.label}: ${tooltipItem.raw}`;
          },
        },
      },
    },
  };

  const handleFileFilter = async () => {
    if (!dateFilter ||!typeFilter) {
      toast({
        title: "Missing Information",
        description: "Please select a date and file type before filtering.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    const [year, month, day] = dateFilter.split("-");
    const formattedDate = `${month}-${day}-${year}`;
    try {
      let response = await axios.get(
        "http://127.0.0.1:8000/edi/files_filter/",
        {
          params: {
            file_date: formattedDate,
            file_type: typeFilter,
          },
        }
      );
      console.log(response);
      setEdiFiles(response.data);
    } catch (error) {
      console.log(error);
    }
  };


  useEffect(() => {
    getFiles();
  }, []);

  return (
    <Box bg="blue.50" minH="100vh" p={8} mt={45}>
      <Heading mb={6} size={"lg"}>EDI Dashboard</Heading>

      {/* Filter Section */}
      <Flex mb={8} gap={4} align="center">
        <Select
          w={"20%"}
          size={"sm"}
          placeholder="Filter by Type"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          bg="blue.100"
          color="blue.700"
        >
          <option value="834">834</option>
          <option value="835">835</option>
          {/* Add more options as needed */}
        </Select>

        <Input
          w={"20%"}
          size={"sm"}
          type="date"
          placeholder="Filter by Date"
          value={dateFilter}
          onChange={(e) => setDateFilter(e.target.value)}
          bg="blue.100"
          color="blue.700"
        />

        <Button size={"sm"} colorScheme="blue" onClick={handleFileFilter}>Apply Filters</Button>
        <Button size={"sm"} variant="outline" colorScheme="blue" onClick={resetFilters}>Reset Filters</Button>
      </Flex>

      {/* Pie Chart Section */}
      <Box m={"auto"} mb={8} h="25%" maxW="25%">
        <Pie data={pieChartData} options={pieChartOptions} />
      </Box>

      {/* Processed Files Section */}
      <Box mb={8}>
        <Heading size="md" mb={4}>Processed Files</Heading>
        <Table colorScheme='blue' size={"sm"}>
          <Thead bg={"blue.400"}>
            <Tr>
              <Th color={"white"}>File Name</Th>
              <Th color={"white"}>File Type</Th>
              <Th color={"white"}>File Date</Th>
            </Tr>
          </Thead>
          <Tbody>
            {processedFiles.map((file, index) => (
              <Tr key={index}>
                <Td>{file.file_name}</Td>
                <Td>{file.file_type}</Td>
                <Td>{file.file_date}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {/* Failed Files Section */}
      <Box>
        <Heading size="md" mb={4}>Failed Files</Heading>
        <Table colorScheme='red' size={"sm"}>
          <Thead bg={"red.400"}>
            <Tr>
              <Th color={"white"}>File Name</Th>
              <Th color={"white"}>File Type</Th>
              <Th color={"white"}>File Date</Th>
            </Tr>
          </Thead>
          <Tbody>
            {failedFiles.map((file, index) => (
              <Tr key={index}>
                <Td>{file.file_name}</Td>
                <Td>{file.file_type}</Td>
                <Td>{file.file_date}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
    </Box>
  );
};

export default Dashboard;
