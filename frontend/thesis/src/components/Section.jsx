import React from "react";
import { Box, Container, Typography } from "@mui/material";

const Section = ({ header, children }) => {
  return (
    <Box
      component="section"
      sx={{
        backgroundColor: "#F1F5F9",
        height: "80vh",
        minWidth: 0,
        flex: 1,
        padding: "1rem",
        paddingRight: 0,
        borderRadius: "15px",
        display: "flex",
        flexDirection: "column",
        boxSizing: "border-box"
      }}
    >
      <Typography sx={{ paddingBottom: "1rem" }}>{header}</Typography>
      <Box
        sx={{
          overflowY: "auto",
          overflowX: "hidden",
          paddingRight: "1rem",
          flex: 1,
          minHeight: 0
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Section;
