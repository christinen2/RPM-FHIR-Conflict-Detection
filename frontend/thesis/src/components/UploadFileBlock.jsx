import React, { useRef, useState } from "react";
import { Box, Button, Typography } from "@mui/material";

const UploadFileBlock = ({ selectedFile, setSelectedFile, nextStep }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file) {
      setSelectedFile(file);
    }
  };

  const handleEvaluateBtnClick = () => {
    if (selectedFile === null) {
      console.log("need to add an err msg here");
    } else {
      nextStep();
    }
  };

  return (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 2
      }}
    >
      TODO
    </Box>
  );
};

export default UploadFileBlock;
