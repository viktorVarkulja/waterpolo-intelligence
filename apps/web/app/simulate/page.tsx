import EmptyStateCard from "../../components/EmptyStateCard";

export default function SimulatePage() {
  return (
    <EmptyStateCard
      title="Simulation coming soon"
      description="Final Four simulation and bracket odds will be available once predictive models are wired in."
      actionLabel="Back to teams"
      actionHref="/teams"
    />
  );
}
