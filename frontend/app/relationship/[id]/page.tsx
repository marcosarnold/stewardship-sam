import Link from "next/link";

export default async function RelationshipStubPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <main>
      <p>
        <Link href="/">&larr; Back to Today</Link>
      </p>
      <h1>Relationship view for constituent {id}</h1>
      <p className="empty-state">
        The full relationship view is not built yet (see issues/005-relationship-view-evidence-card.md).
      </p>
    </main>
  );
}
