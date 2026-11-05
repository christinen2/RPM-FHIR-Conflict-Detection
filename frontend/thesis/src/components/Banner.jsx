import React from "react";
import { Box, Container, Typography } from "@mui/material";

const Banner = ({ onClick }) => {
  return (
    <Box
      component="header"
      sx={{
        width: "79vw",
        padding: "1rem",
        cursor: "pointer"
      }}
      onClick={onClick}
    >
      <Container maxWidth="lg" sx={{ margin: 0 }}>
        <Typography
          variant="h4"
          component="h1"
          sx={{
            fontWeight: 600,
            mb: 0.5
          }}
        >
          CarePlan Conflict Detector
        </Typography>
      </Container>
    </Box>
  );
};

export default Banner;
