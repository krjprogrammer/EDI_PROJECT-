import { Flex, Icon, Text } from "@chakra-ui/react";
import React from "react";
import { Link } from "react-router-dom";
import { MdCloudUpload } from "react-icons/md";
import { FaBell, FaUserCircle } from "react-icons/fa";
import Cookies from "js-cookie";

const Navbar = () => {
  const handleLogout = async () => {
    
    Cookies.remove("editoken");

    window.location.reload();
  };

  return (
    <Flex
      justifyContent="space-between"
      alignItems="center"
      bg="blue.600"
      color="white"
      p={4}
      borderRadius="sm"
      position={"fixed"}
      w={"100%"}
      top={0}
      zIndex={100}
      fontFamily={"rajdhani"}
    >
      <Link to={"/"}>
        <Flex cursor={"pointer"} alignItems="center">
          <Icon as={MdCloudUpload} boxSize={6} mr={2} />
          <Text fontWeight="bold" fontSize="lg">
            EDI
          </Text>
        </Flex>
      </Link>

      <Flex alignItems="center" gap={4}>
        <Link to={"/"}>
          <Text cursor={"pointer"}>Home</Text>
        </Link>
        <Link to={"/archived"}>
          <Text cursor={"pointer"}>Archived</Text>
        </Link>
        <Link to={"/dashboard"}>
          <Text cursor={"pointer"}>Dashboard</Text>
        </Link>
        <Icon as={FaBell} boxSize={5} cursor="pointer" />
        <Flex alignItems="center">
          <Icon cursor={"pointer"} as={FaUserCircle} boxSize={5} mr={2} />

          {/* <Text>Akshay</Text> */}
          <Text cursor={"pointer"} onClick={handleLogout}>Log out</Text>
        </Flex>
      </Flex>
    </Flex>
  );
};

export default Navbar;
