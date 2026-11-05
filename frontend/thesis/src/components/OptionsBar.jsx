import { Box, FormControlLabel, Checkbox, Button } from "@mui/material";
import React from "react";
import { ViewType } from "../pages/EvaluatePage";

const OptionsBar = ({ view, setView, checked, setChecked }) => {
  return (
    <Box
      sx={{
        display: "flex",
        width: "80%",
        justifyContent: "space-evenly"
      }}
    >
      <FormControlLabel
        control={
          <Checkbox
            checked={checked}
            onChange={(event) => setChecked(event.target.checked)}
          />
        }
        label="Show FHIR Code"
      />

      <Button variant="contained" onClick={() => setView(ViewType.LIST)}>
        List View
      </Button>
      <Button variant="contained" onClick={() => setView(ViewType.THRESHOLDS)}>
        Threshold View
      </Button>
    </Box>
  );
};

export default OptionsBar;
