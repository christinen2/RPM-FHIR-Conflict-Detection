import React, { useEffect, useState } from "react";
import { Box } from "@mui/material";
import SummaryStatBox from "./SummaryStatBox";
import { countResources } from "../fn";

const ConflictSummary = ({ res, selectedFile }) => {
  const [pd, setPd] = useState(0);
  const [act, setAct] = useState(0);
  const [conflict, setConflict] = useState(0);

  useEffect(() => {
    if (!res) {
      setPd(0);
      setAct(0);
      setConflict(0);
      return;
    }

    const fetchCounts = async () => {
      try {
        const counts = await countResources(selectedFile);

        setPd(counts["plan_defs"]);
        setAct(counts["act_defs"]);
        setConflict(res.conflicts.length);
      } catch (error) {
        console.error("Error fetching resource counts:", error);
      }
    };

    fetchCounts();
  }, [res, selectedFile]);
  return (
    <Box
      sx={{
        width: "79vw",
        height: "11h",
        backgroundColor: "#F1F5F9",
        borderRadius: "15px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-evenly"
      }}
    >
      <SummaryStatBox number={pd} statname="plan definition(s)" />
      <SummaryStatBox number={act} statname="activites" />
      <SummaryStatBox number={conflict} statname="conflicts" />
    </Box>
  );
};

export default ConflictSummary;
