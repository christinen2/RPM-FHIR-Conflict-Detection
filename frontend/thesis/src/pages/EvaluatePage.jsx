import React, { useEffect, useRef, useState } from "react";
import { Box } from "@mui/material";
import FhirCodeBlock from "../components/FhirCodeBlock";
import ConflictList from "../components/ConflictList";
import ConflictSummary from "../components/ConflictSummary";
import OptionsBar from "../components/OptionsBar";
import ThresholdView from "../components/ThresholdView";
import { findConflicts } from "../fn";

export const ViewType = {
  LIST: "list",
  THRESHOLDS: "thresholds"
};

const EvaluatePage = ({ selectedFile }) => {
  const [view, setView] = useState(ViewType.LIST);
  const [checked, setChecked] = useState(true);
  const [res, setRes] = useState();

  useEffect(() => {
    if (!selectedFile) {
      setRes({});
      return;
    }

    const fetchConflicts = async () => {
      try {
        const result = await findConflicts(selectedFile);
        setRes(result);
      } catch (error) {
        console.error("Error finding conflicts:", error);
        setRes({});
      }
    };

    fetchConflicts();
  }, [selectedFile?.name, selectedFile?.size, selectedFile?.lastModified]);

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
      <ConflictSummary res={res} selectedFile={selectedFile} />
      <OptionsBar
        view={view}
        setView={setView}
        checked={checked}
        setChecked={setChecked}
      />

      <Box
        sx={{
          flexDirection: "row",
          display: "flex",
          width: "80%",
          gap: 2
        }}
      >
        {checked && <FhirCodeBlock selectedFile={selectedFile} />}
        {view === ViewType.LIST && <ConflictList res={res} />}
        {view === ViewType.THRESHOLDS && <ThresholdView res={res} />}
      </Box>
    </Box>
  );
};

export default EvaluatePage;
