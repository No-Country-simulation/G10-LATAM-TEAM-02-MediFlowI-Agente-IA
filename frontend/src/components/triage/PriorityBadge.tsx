
const PriorityBadge = ({ priority = "NORMAL" }: { priority?: string }) => {
  const normPriority = (priority || "").toUpperCase();

  if (normPriority === "URGENTE") {
    return (
      <span className="badge bg-danger bg-opacity-10 text-danger border border-danger-subtle px-2.5 py-1 rounded-pill fw-bold text-nowrap">
        ● URGENTE
      </span>
    );
  }

  if (normPriority === "PRIORITARIO" || normPriority === "AMBIGUO") {
    return (
      <span className="badge bg-warning bg-opacity-15 text-warning border border-warning-subtle px-2.5 py-1 rounded-pill fw-bold text-nowrap">
        ● AMBIGUO
      </span>
    );
  }

  return (
    <span className="badge bg-success bg-opacity-10 text-success border border-success-subtle px-2.5 py-1 rounded-pill fw-bold text-nowrap">
      ● RUTINA
    </span>
  );
};

export default PriorityBadge;
