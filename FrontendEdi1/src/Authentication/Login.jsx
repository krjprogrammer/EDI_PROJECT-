// import React, { useState } from "react";
// import {
//   Box,
//   Button,
//   FormControl,
//   FormLabel,
//   Input,
//   InputGroup,
//   InputRightElement,
//   Heading,
//   VStack,
//   useToast,
//   Image,
//   Flex,
//   Text,
// } from "@chakra-ui/react";
// import { useNavigate } from "react-router-dom";
// import loginIllus from "../assets/login.jpg";
// import axios from "axios";
// import Cookies from "js-cookie";

// function Login() {
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [showPassword, setShowPassword] = useState(false);
//   const [loader, setLoader] = useState(false);
//   const navigate = useNavigate();
//   const toast = useToast();

//   const handleLogin = async (e) => {
//     e.preventDefault();
//     if (!email || !password) {
//       toast({
//         title: "Error",
//         description: "Please fill in all fields",
//         status: "error",
//         duration: 3000,
//         isClosable: true,
//       });
//       return;
//     }
//     try {
//       setLoader(true);
//       // Simulate login API call
//       let resposne = await axios.post("http://127.0.0.1:8000/edi/login/", {
//         username: email,
//         password: password,
//       });
//       console.log(resposne);
//       if(resposne.data.message == "Login successful"){
//         setLoader(false);
//         Cookies.set("editoken", resposne.data.username, { expires: 7 });
//         toast({
//           title: "Success",
//           description: "Logged in successfully",
//           status: "success",
//           duration: 3000,
//           isClosable: true,
//         });
//         navigate("/");
//       }
//       // if (email === "admin@example.com" && password === "password") {
//       //   toast({
//       //     title: "Success",
//       //     description: "Logged in successfully",
//       //     status: "success",
//       //     duration: 3000,
//       //     isClosable: true,
//       //   });
//       //   navigate("/dashboard");
//       // } else {
//       //   toast({
//       //     title: "Error",
//       //     description: "Invalid credentials",
//       //     status: "error",
//       //     duration: 3000,
//       //     isClosable: true,
//       //   });
//       // }
//     } catch (error) {
//       setLoader(false);
//       console.log(error);
//     }
//   };

//   return (
//     <Flex
//       height="100vh"
//       alignItems="center"
//       justifyContent="center"
//       bg="gray.100"
//     >
//       <Box
//         display={{ base: "none", md: "block" }}
//         w="50%"
//         bg="blue.600"
//         color="white"
//         height="100%"
//         p={8}
//       >
//         <Flex
//           direction="column"
//           alignItems="center"
//           justifyContent="center"
//           height="100%"
//         >
//           <Image
//             src={loginIllus}
//             alt="Illustration"
//             boxSize="80%"
//             objectFit="contain"
//             mb={6}
//           />
//           <Text fontSize="xl" fontWeight="bold">
//             Welcome Back!
//           </Text>
//           <Text fontSize="md" mt={2} textAlign="center">
//             Enter your credentials to access your account
//           </Text>
//         </Flex>
//       </Box>
//       <Box
//         w={{ base: "90%", md: "40%" }}
//         p={8}
//         margin={20}
//         bg="white"
//         borderRadius="lg"
//         boxShadow="lg"
//       >
//         <VStack as="form" onSubmit={handleLogin} spacing={6}>
//           <Heading size="lg" color="blue.600" mb={2}>
//             Login
//           </Heading>
//           <FormControl id="email" isRequired>
//             <FormLabel>Username</FormLabel>
//             <Input
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//               bg="gray.50"
//               placeholder="Enter your username"
//             />
//           </FormControl>
//           <FormControl id="password" isRequired>
//             <FormLabel>Password</FormLabel>
//             <InputGroup>
//               <Input
//                 type={showPassword ? "text" : "password"}
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 bg="gray.50"
//                 placeholder="Enter your password"
//               />
//               <InputRightElement width="4.5rem">
//                 <Button
//                   h="1.75rem"
//                   size="sm"
//                   onClick={() => setShowPassword(!showPassword)}
//                 >
//                   {showPassword ? "Hide" : "Show"}
//                 </Button>
//               </InputRightElement>
//             </InputGroup>
//           </FormControl>
//           <Button isLoading={loader} colorScheme="blue" type="submit" width="full" mt={4}>
//             Login
//           </Button>
//         </VStack>
//       </Box>
//     </Flex>
//   );
// }

// export default Login;

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  FormControl,
  Input,
  Text,
  VStack,
  Grid,
  GridItem,
  useToast,
  Avatar,
  Stack,
  Heading,
  HStack,
} from "@chakra-ui/react";
import axios from "axios";
import loginIllus from "../assets/login.jpg";


const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [inputOtp, setInputOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [errors, setErrors] = useState({});
  const [loader, setLoader] = useState(false);

  const navigate = useNavigate();
  const toast = useToast();

  const handleSendOtp = async () => {
    if (!email || !password) {
      setErrors({ email: "Email and password are required" });
      return;
    }
    setErrors({});
    try {
      setLoader(true);
      const response = await axios.post(`http://127.0.0.1:8000/edi/send-otp/`, {
        email,
        password,
      });

      toast({
        title: "OTP sent",
        description: "Please check your email for the OTP.",
        status: "success",
        duration: 5000,
        isClosable: true,
      });
      setOtpSent(true);
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Invalid credentials.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoader(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    if (!inputOtp) {
      setErrors({ otp: "OTP is required" });
      return;
    }

    try {
      setLoader(true);
      const response = await axios.post(`http://127.0.0.1:8000/auth/otp-login/`, {
        email,
        otp: inputOtp,
      });

      const { token, username } = response.data;

      localStorage.setItem("token", token);
      toast({
        title: "Login successful",
        description: `Welcome, ${username}!`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });

      setEmail("");
      setPassword("");
      setInputOtp("");
      navigate("/dashboard");
    } catch (error) {
      setErrors({ otp: "Invalid OTP" });
      toast({
        title: "Login failed",
        description: error.response?.data?.error || "Invalid OTP or email.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoader(false);
    }
  };

  return (
    <Grid templateColumns="60% 40%" h="100vh">
      <GridItem
        bgImage={loginIllus}
        bgPosition="center"
        bgRepeat="no-repeat"
        bgSize="cover"
      />
      <GridItem display="flex" justifyContent="center" alignItems="center">
        <Box className="max-w-md p-8" bg="white" mt={30} rounded="md" w="100%">
          <Stack
            flexDir="column"
            mb="2"
            justifyContent="center"
            alignItems="center"
          >
            <Avatar bg="blue.500" />
            <Heading
              mb={10}
              fontSize={"3xl"}
              fontWeight="bold"
              color="blue.500"
              textAlign="center"
            >
              Login to your Account
            </Heading>
            <form onSubmit={handleSubmit} mt="10">
              <VStack spacing="4">
                <FormControl id="email" isInvalid={errors.email} w="100%">
                  <Input
                    type="email"
                    value={email}
                    border={"1px solid gray"}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    focusBorderColor="blue.500"
                  />
                </FormControl>
                {!otpSent && (
                  <FormControl id="password" isInvalid={errors.password} w="100%">
                    <Input
                      type="password"
                      value={password}
                      border={"1px solid gray"}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      focusBorderColor="blue.500"
                    />
                  </FormControl>
                )}
                {otpSent && (
                  <FormControl id="otp" isInvalid={errors.otp} w="100%">
                    <Input
                      type="text"
                      value={inputOtp}
                      border={"1px solid gray"}
                      onChange={(e) => setInputOtp(e.target.value)}
                      placeholder="Enter OTP"
                      focusBorderColor="blue.500"
                    />
                  </FormControl>
                )}
                {!otpSent ? (
                  <Button
                    onClick={handleSendOtp}
                    isLoading={loader}
                    bg="blue.500"
                    color="white"
                    _hover={{ bg: "blue.600" }}
                    w="100%"
                  >
                    Send OTP
                  </Button>
                ) : (
                  <HStack w="100%" spacing="4">
                    <Button
                      type="submit"
                      isLoading={loader}
                      bg="blue.500"
                      color="white"
                      _hover={{ bg: "blue.600" }}
                      w="100%"
                    >
                      Login
                    </Button>
                  </HStack>
                )}
              </VStack>
            </form>
          </Stack>
        </Box>
      </GridItem>
    </Grid>
  );
};

export default Login;
