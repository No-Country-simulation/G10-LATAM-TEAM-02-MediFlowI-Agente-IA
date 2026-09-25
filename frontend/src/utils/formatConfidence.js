/**
 * Formats a confidence score into percentage and risk level (Alta, Media, Baja).
 * @param {number|string} score - Score as decimal (0.94) or percentage (94)
 */
export const formatConfidence = (score) => {
  if (score === null || score === undefined || isNaN(score)) {
    return {
      percentage: 0,
      formattedText: "0%",
      level: "Baja",
      variant: "danger",
      badgeClass: "bg-danger",
      progressClass: "bg-danger"
    };
  }

  let val = Number(score);
  // If provided as a decimal between 0 and 1
  if (val <= 1.0 && val > 0) {
    val = val * 100;
  }

  const rounded = Math.round(val);

  if (rounded >= 80) {
    return {
      percentage: rounded,
      formattedText: `${rounded}%`,
      level: "Alta",
      variant: "success",
      badgeClass: "bg-success",
      progressClass: "bg-success"
    };
  } else if (rounded >= 60) {
    return {
      percentage: rounded,
      formattedText: `${rounded}%`,
      level: "Media",
      variant: "warning",
      badgeClass: "bg-warning text-dark",
      progressClass: "bg-warning"
    };
  } else {
    return {
      percentage: rounded,
      formattedText: `${rounded}%`,
      level: "Baja",
      variant: "danger",
      badgeClass: "bg-danger",
      progressClass: "bg-danger"
    };
  }
};
