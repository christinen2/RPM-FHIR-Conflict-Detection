import React, { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";

const SummaryStatBox = ({ number, statname }) => {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        flexDirection: "column",
        alignItems: "center"
      }}
    >
      <Typography variant="h2">{number}</Typography>
      <Typography>{statname}</Typography>
    </Box>
  );
};

export default SummaryStatBox;
