import React from "react";
import { Box, Typography } from "@mui/material";

const RangeVisualisation = ({ conflict }) => {
  const parseBound = (value, index) => {
    if (value == null || value === "") {
      return index === 0 ? -Infinity : Infinity;
    }

    if (typeof value === "string") {
      const trimmed = value.trim().toLowerCase();

      if (trimmed === "-inf" || trimmed === "-infinity") {
        return -Infinity;
      }

      if (
        trimmed === "inf" ||
        trimmed === "+inf" ||
        trimmed === "infinity" ||
        trimmed === "+infinity"
      ) {
        return Infinity;
      }
    }

    return Number(value);
  };

  const parseRange = (range) => {
    if (range == null || range === "") {
      return { min: -Infinity, max: Infinity };
    }

    let values = range;

    if (typeof range === "string") {
      values = range.replace("[", "").replace("]", "").split(",");
    }

    if (!Array.isArray(values)) {
      return { min: -Infinity, max: Infinity };
    }

    return {
      min: parseBound(values[0], 0),
      max: parseBound(values[1], 1)
    };
  };

  const formatBound = (value) => {
    if (value === Infinity) return "∞";
    if (value === -Infinity) return "−∞";
    return value;
  };

  const formatBounds = (bounds = []) =>
    bounds
      .map((bound, index) => formatBound(parseBound(bound, index)))
      .join(", ");

  const range1 = parseRange(conflict.bounds1);
  const range2 = parseRange(conflict.bounds2);

  const finiteValues = [range1.min, range1.max, range2.min, range2.max].filter(
    Number.isFinite
  );

  const dataMin = finiteValues.length ? Math.min(...finiteValues) : 0;

  const dataMax = finiteValues.length ? Math.max(...finiteValues) : 100;

  const padding = Math.max((dataMax - dataMin) * 0.2, 10);

  const min = dataMin - padding;
  const max = dataMax + padding;

  const getPosition = (value) => {
    if (value === -Infinity) return 0;
    if (value === Infinity) return 100;

    const position = ((value - min) / (max - min)) * 100;

    return Math.max(0, Math.min(100, position));
  };

  const overlapMin = Math.max(range1.min, range2.min);
  const overlapMax = Math.min(range1.max, range2.max);

  const hasOverlap = overlapMin <= overlapMax;

  const overlapStart = getPosition(overlapMin);
  const overlapEnd = getPosition(overlapMax);

  const actualOverlapWidth = Math.max(0, overlapEnd - overlapStart);

  const minOverlapWidth = 7;

  let visualOverlapWidth = actualOverlapWidth;
  let visualOverlapStart = overlapStart;

  if (hasOverlap && actualOverlapWidth < minOverlapWidth) {
    visualOverlapWidth = minOverlapWidth;
    visualOverlapStart =
      overlapStart - (minOverlapWidth - actualOverlapWidth) / 2;
  }

  visualOverlapWidth = Math.min(100, visualOverlapWidth);

  visualOverlapStart = Math.max(
    0,
    Math.min(100 - visualOverlapWidth, visualOverlapStart)
  );

  const overlapLabelPosition = Math.min(
    95,
    Math.max(5, visualOverlapStart + visualOverlapWidth / 2)
  );

  const range1Start = getPosition(range1.min);
  const range1End = getPosition(range1.max);

  const range2Start = getPosition(range2.min);
  const range2End = getPosition(range2.max);

  return (
    <Box
      sx={{
        width: "100%",
        display: "flex",
        justifyContent: "center",
        mt: 3
      }}
    >
      <Box
        sx={{
          position: "relative",
          height: "190px",
          width: "90%",
          maxWidth: "900px",
          mx: "auto"
        }}
      >
        {/* Activity 1 label */}
        <Box
          sx={{
            position: "absolute",
            top: 0,
            left: `${range1Start}%`,
            textAlign: "left",
            whiteSpace: "nowrap",
            maxWidth: "45%"
          }}
        >
          <Typography
            sx={{
              fontSize: "0.8rem",
              fontWeight: 600,
              color: "#334155"
            }}
          >
            {conflict.activity1}
          </Typography>

          <Typography
            sx={{
              fontSize: "0.7rem",
              color: "#64748B"
            }}
          >
            [{formatBounds(conflict.bounds1)}]
          </Typography>
        </Box>

        <Box
          sx={{
            position: "absolute",
            top: "48px",
            left: `${range1Start}%`,
            width: `${Math.max(0, range1End - range1Start)}%`,
            height: "14px",
            backgroundColor: "#94A3B8",
            borderRadius: "7px"
          }}
        />

        <Box
          sx={{
            position: "absolute",
            top: "85px",
            left: `${range2Start}%`,
            textAlign: "left",
            whiteSpace: "nowrap",
            maxWidth: "45%"
          }}
        >
          <Typography
            sx={{
              fontSize: "0.8rem",
              fontWeight: 600,
              color: "#334155"
            }}
          >
            {conflict.activity2}
          </Typography>

          <Typography
            sx={{
              fontSize: "0.7rem",
              color: "#64748B"
            }}
          >
            [{formatBounds(conflict.bounds2)}]
          </Typography>
        </Box>

        {/* Activity 2 range */}
        <Box
          sx={{
            position: "absolute",
            top: "130px",
            left: `${range2Start}%`,
            width: `${Math.max(0, range2End - range2Start)}%`,
            height: "14px",
            backgroundColor: "#64748B",
            borderRadius: "7px"
          }}
        />

        {/* Overlap highlight */}
        {hasOverlap && (
          <>
            <Box
              sx={{
                position: "absolute",
                top: "65px",
                left: `${overlapStart}%`,
                width: `${Math.max(0, overlapEnd - overlapStart)}%`,
                height: "6px",
                backgroundColor: "#2563EB",
                borderRadius: "3px",
                zIndex: 2
              }}
            />

            <Box
              sx={{
                position: "absolute",
                top: "153px",
                left: `${overlapLabelPosition}%`,
                transform: "translateX(-50%)",
                textAlign: "center",
                whiteSpace: "nowrap"
              }}
            >
              <Typography
                sx={{
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  color: "#1D4ED8"
                }}
              >
                OVERLAP
              </Typography>

              <Typography
                sx={{
                  fontSize: "0.7rem",
                  color: "#475569"
                }}
              >
                [{formatBound(overlapMin)}, {formatBound(overlapMax)}]
              </Typography>
            </Box>
          </>
        )}

        {/* Horizontal reference axis */}
        <Box
          sx={{
            position: "absolute",
            top: "68px",
            left: 0,
            right: 0,
            height: "2px",
            backgroundColor: "#CBD5E1",
            zIndex: 1
          }}
        />

        {/* Display scale endpoints */}
        <Typography
          sx={{
            position: "absolute",
            top: "72px",
            left: 0,
            fontSize: "0.7rem",
            color: "#475569"
          }}
        >
          {Number(min.toFixed(2))}
        </Typography>

        <Typography
          sx={{
            position: "absolute",
            top: "72px",
            right: 0,
            fontSize: "0.7rem",
            color: "#475569"
          }}
        >
          {Number(max.toFixed(2))}
        </Typography>
      </Box>
    </Box>
  );
};

export default RangeVisualisation;
