"use client";

import cytoscape, { type Core } from "cytoscape";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchCommunityGraph } from "@/lib/api";
import type { CommunityGraphNode } from "@/lib/types";

export default function CommunityGraph({ communityId }: { communityId: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const router = useRouter();
  const [omittedCount, setOmittedCount] = useState(0);
  const [selected, setSelected] = useState<CommunityGraphNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [showList, setShowList] = useState(false);
  const [nodes, setNodes] = useState<CommunityGraphNode[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchCommunityGraph(communityId)
      .then((graph) => {
      if (cancelled || graph === null || !containerRef.current) return;

      setOmittedCount(graph.omitted_count);
      setNodes(graph.nodes);

      const elements = [
        ...graph.nodes.map((n) => ({
          data: { ...n, label: n.name },
        })),
        ...graph.edges.map((e) => ({ data: { source: e.source, target: e.target } })),
      ];

      const cy = cytoscape({
        container: containerRef.current,
        elements,
        style: [
          {
            selector: 'node[type = "community"]',
            style: {
              shape: "diamond",
              "background-color": "#1d4ed8",
              label: "data(label)",
              "font-size": 8,
              width: 24,
              height: 24,
            },
          },
          {
            selector: "node[?is_center]",
            style: { width: 44, height: 44, "background-color": "#1d4ed8", "font-size": 11, "font-weight": "bold" },
          },
          {
            selector: 'node[type = "person"]',
            style: {
              shape: "ellipse",
              "background-color": "#9ca3af",
              width: 12,
              height: 12,
              label: "",
            },
          },
          {
            selector: "node[?is_connector]",
            style: {
              "background-color": "#f59e0b",
              width: 20,
              height: 20,
              "border-width": 2,
              "border-color": "#b45309",
              label: "data(label)",
              "font-size": 7,
            },
          },
          {
            selector: "edge",
            style: { width: 1, "line-color": "#e5e7eb", "curve-style": "haystack" },
          },
        ],
        layout: { name: "concentric", concentric: (n: any) => (n.data("is_center") ? 3 : n.data("is_connector") ? 2 : 1), levelWidth: () => 1, minNodeSpacing: 8 },
      });

      cy.on("tap", "node", (evt) => {
        const data = evt.target.data() as CommunityGraphNode;
        if (data.type === "person" && data.entity_id) {
          router.push(`/relationship/${data.entity_id}`);
        } else if (data.type === "community" && !data.is_center && data.community_id) {
          router.push(`/community/${data.community_id}`);
        } else {
          setSelected(data);
        }
      });

      cy.on("mouseover", "node[?is_connector]", (evt) => {
        setSelected(evt.target.data() as CommunityGraphNode);
      });

      cyRef.current = cy;
      setLoading(false);
      })
      .catch(() => {
        if (!cancelled) {
          setError("Could not reach the Stewardship Sam API. Is the backend running?");
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
      cyRef.current?.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [communityId]);

  return (
    <div>
      <div className="graph-legend">
        <span>
          <span className="legend-swatch legend-center" /> This community
        </span>
        <span>
          <span className="legend-swatch legend-connector" /> Connector (spans other communities)
        </span>
        <span>
          <span className="legend-swatch legend-person" /> Member
        </span>
        <span>
          <span className="legend-swatch legend-bridge" /> Bridge community
        </span>
      </div>
      <p className="held-back-caveat">
        An edge is shared institutional context, not friendship or influence.
      </p>
      {omittedCount > 0 && <p className="held-back-caveat">+{omittedCount} more members not shown</p>}

      {selected && (
        <p className="queue-summary">
          <strong>{selected.name}</strong>
          {selected.basis ? `: ${selected.basis}` : ""}
        </p>
      )}

      {error && <p className="error-state">{error}</p>}
      <div ref={containerRef} className="community-graph-canvas" hidden={showList || !!error} />
      {loading && !showList && !error && <p className="empty-state">Loading graph&hellip;</p>}

      <button type="button" className="show-all-button" onClick={() => setShowList(!showList)}>
        {showList ? "Show graph" : "Show list view"}
      </button>

      {showList && (
        <ul className="community-list">
          {nodes
            .filter((n) => n.type === "person")
            .map((n) => (
              <li key={n.id} className="community-membership">
                <a href={`/relationship/${n.entity_id}`} className="community-membership-name">
                  {n.name}
                </a>
                {n.is_connector && <span className="community-membership-count">{n.basis}</span>}
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}
