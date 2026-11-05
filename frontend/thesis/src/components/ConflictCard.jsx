import React, { useState } from "react";
import { Box, Typography, Collapse, IconButton, Divider } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

const ConflictCard = ({ index, conflict }) => {
  const [open, setOpen] = useState(false);

  console.log(conflict);

  const handleClick = () => {
    setOpen((prev) => !prev);
  };

  return (
    <Box
      sx={{
        backgroundColor: "#FFFFFF",
        border: "1px solid #E2E8F0",
        borderRadius: 3,
        overflow: "hidden",
        transition: "border-color 0.2s, box-shadow 0.2s",
        "&:hover": {
          borderColor: "#94A3B8",
          boxShadow: "0 2px 8px rgba(15, 23, 42, 0.06)"
        }
      }}
    >
      <Box
        onClick={handleClick}
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 2,
          p: 2,
          cursor: "pointer"
        }}
      >
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography
            variant="overline"
            sx={{
              color: "#64748B",
              fontWeight: 600,
              letterSpacing: 1
            }}
          >
            Conflict {index + 1}
          </Typography>

          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 600,
              color: "#1E293B",
              lineHeight: 1.5
            }}
          >
            {conflict.activity1} and {conflict.activity2}
          </Typography>

          <Typography variant="body2" sx={{ color: "#64748B", mt: 0.5 }}>
            {conflict.type || "Threshold conflict"}
          </Typography>
        </Box>

        <IconButton
          size="small"
          aria-label={
            open ? "Collapse conflict details" : "Expand conflict details"
          }
          sx={{
            color: "#64748B",
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.2s"
          }}
        >
          <ExpandMoreIcon />
        </IconButton>
      </Box>

      <Collapse in={open}>
        <Divider sx={{ borderColor: "#E2E8F0" }} />

        <Box
          sx={{
            p: 2,
            backgroundColor: "#F8FAFC",
            display: "flex",
            flexDirection: "column",
            gap: 2
          }}
        >
          <Box>
            <Typography
              variant="caption"
              sx={{
                color: "#64748B",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: 0.5
              }}
            >
              Range 1
            </Typography>
            <Typography variant="body2" sx={{ color: "#334155", mt: 0.5 }}>
              {conflict.bounds1
                .map((bound, index) =>
                  bound === null ? (index === 0 ? "-inf" : "inf") : bound
                )
                .join(", ")}
            </Typography>
          </Box>

          <Box>
            <Typography
              variant="caption"
              sx={{
                color: "#64748B",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: 0.5
              }}
            >
              Range 2
            </Typography>
            <Typography variant="body2" sx={{ color: "#334155", mt: 0.5 }}>
              {conflict.bounds2
                .map((bound, index) =>
                  bound === null ? (index === 0 ? "-inf" : "inf") : bound
                )
                .join(", ")}
            </Typography>
          </Box>

          <Box>
            <Typography
              variant="caption"
              sx={{
                color: "#64748B",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: 0.5
              }}
            >
              Description
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: "#334155",
                mt: 0.5,
                lineHeight: 1.7
              }}
            >
              {conflict.detail}
            </Typography>
          </Box>
        </Box>
      </Collapse>
    </Box>
  );
};

export default ConflictCard;
