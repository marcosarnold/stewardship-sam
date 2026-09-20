"use client";

import { useEffect, useRef, useState } from "react";
import { extractNote, fetchLatestNote, saveNote } from "@/lib/api";
import type { ExtractedNote, SavedNote } from "@/lib/types";

export default function PostCallNote({ entityId }: { entityId: number }) {
  const [note, setNote] = useState("");
  const [draft, setDraft] = useState<ExtractedNote | null>(null);
  const [saved, setSaved] = useState<SavedNote | null>(null);
  const [recording, setRecording] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    fetchLatestNote(entityId).then(setSaved);

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((r: any) => r[0].transcript)
          .join(" ");
        setNote((current) => (current ? `${current} ${transcript}` : transcript));
      };
      recognition.onend = () => setRecording(false);
      recognitionRef.current = recognition;
    }
  }, [entityId]);

  function toggleRecording() {
    if (!recognitionRef.current) return;
    if (recording) {
      recognitionRef.current.stop();
      setRecording(false);
    } else {
      recognitionRef.current.start();
      setRecording(true);
    }
  }

  async function handleExtract() {
    if (!note.trim()) return;
    const result = await extractNote(entityId, note);
    setDraft(result);
  }

  async function handleConfirm() {
    if (!draft) return;
    const result = await saveNote(entityId, draft, note);
    setSaved(result);
    setDraft(null);
    setNote("");
  }

  return (
    <div>
      {speechSupported && (
        <p className="relationship-subline">
          <button type="button" className="show-all-button" onClick={toggleRecording}>
            {recording ? "⏹ Stop recording" : "🎤 Record note"}
          </button>{" "}
          {recording && <span className="community-badge">Recording&hellip;</span>}
        </p>
      )}

      <textarea
        className="ask-sam-input"
        style={{ width: "100%", minHeight: "4rem" }}
        placeholder="Type or dictate a post-call note..."
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />

      <div className="queue-item-actions">
        <button type="button" className="show-all-button" onClick={handleExtract} disabled={!note.trim()}>
          Extract fields
        </button>
      </div>

      {draft && (
        <div className="action-brief">
          <p className="relationship-subline">Review before saving -- nothing is kept until you confirm.</p>
          <label>
            Interest
            <input
              className="ask-sam-input"
              style={{ width: "100%" }}
              value={draft.interest ?? ""}
              onChange={(e) => setDraft({ ...draft, interest: e.target.value || null })}
            />
          </label>
          <label>
            Communication preference
            <select
              className="ask-sam-input"
              value={draft.communication_preference ?? ""}
              onChange={(e) =>
                setDraft({ ...draft, communication_preference: (e.target.value || null) as any })
              }
            >
              <option value="">Not on file</option>
              <option value="phone">Phone</option>
              <option value="email">Email</option>
              <option value="text">Text (preference only -- not a supported outreach channel)</option>
            </select>
          </label>
          <label>
            Solicitation status
            <select
              className="ask-sam-input"
              value={draft.solicitation_status ?? ""}
              onChange={(e) => setDraft({ ...draft, solicitation_status: (e.target.value || null) as any })}
            >
              <option value="">Not on file</option>
              <option value="not_currently_interested">Not currently interested</option>
            </select>
          </label>
          <label>
            Follow-up date
            <input
              type="date"
              className="ask-sam-input"
              value={draft.follow_up_date ?? ""}
              onChange={(e) => setDraft({ ...draft, follow_up_date: e.target.value || null })}
            />
          </label>
          <div className="queue-item-actions">
            <button type="button" className="show-all-button" onClick={handleConfirm}>
              Confirm and save
            </button>
            <button type="button" className="dismiss-button" onClick={() => setDraft(null)}>
              Discard
            </button>
          </div>
        </div>
      )}

      {saved && (
        <p className="held-back-caveat">
          Saved memory: interest={saved.interest ?? "Not on file"}, preference=
          {saved.communication_preference ?? "Not on file"}, status={saved.solicitation_status ?? "Not on file"},
          follow-up={saved.follow_up_date ?? "Not on file"}
        </p>
      )}
    </div>
  );
}
