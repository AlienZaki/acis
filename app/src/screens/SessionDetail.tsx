/**
 * SessionDetail — view a completed session OR watch a live session.
 *
 * Live mode (live=true):
 *   Shows timer, live transcript feed, live cue chips, Stop button.
 *   On Stop → triggers summarisation → navigates to AI summary tab.
 *
 * Completed mode (live=false):
 *   Two tabs: "AI Summary" | "Transcript".
 *   AI Summary: prose, keypoints accordion, action items, cue chips.
 *   Transcript: timestamped utterance list.
 */

import React, { useCallback, useState } from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { RootStackParamList } from "../navigation";
import { useSessionStore } from "../store/sessions";
import { CueChip } from "../components/CueChip";

type Props = NativeStackScreenProps<RootStackParamList, "SessionDetail">;

export function SessionDetail({ route, navigation }: Props) {
  const { sessionId, live } = route.params;
  const session = useSessionStore((s) => s.sessions.find((x) => x.id === sessionId));
  const stopSession = useSessionStore((s) => s.stopSession);
  const [tab, setTab] = useState<"summary" | "transcript">("summary");

  const handleStop = useCallback(async () => {
    await stopSession(sessionId);
  }, [sessionId, stopSession]);

  if (!session) return null;

  return (
    <View style={styles.root}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.back}>‹ Back</Text>
        </TouchableOpacity>
        <Text style={styles.title} numberOfLines={1}>{session.name}</Text>
      </View>

      {live ? (
        /* Live session view */
        <View style={styles.live}>
          <Text style={styles.timer}>{session.elapsed ?? "00:00:00"}</Text>
          <Text style={styles.listeningLabel}>Listening…</Text>
          <ScrollView style={styles.liveCues}>
            {(session.cues ?? []).slice(-3).map((c) => (
              <CueChip key={c.cue_id} cue={c} />
            ))}
          </ScrollView>
          <TouchableOpacity style={styles.stopBtn} onPress={handleStop}>
            <Text style={styles.stopBtnText}>Stop</Text>
          </TouchableOpacity>
        </View>
      ) : (
        /* Completed session view */
        <>
          <View style={styles.tabs}>
            {(["summary", "transcript"] as const).map((t) => (
              <TouchableOpacity key={t} style={[styles.tab, tab === t && styles.tabActive]} onPress={() => setTab(t)}>
                <Text style={[styles.tabText, tab === t && styles.tabTextActive]}>
                  {t === "summary" ? "AI Summary" : "Transcript"}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 40 }}>
            {tab === "summary" ? (
              <SummaryTab session={session} />
            ) : (
              <TranscriptTab session={session} />
            )}
          </ScrollView>
        </>
      )}
    </View>
  );
}

function SummaryTab({ session }: { session: any }) {
  return (
    <View style={styles.summaryRoot}>
      {session.summary ? (
        <>
          <Text style={styles.sectionLabel}>CONVERSATION SUMMARY</Text>
          <Text style={styles.prose}>{session.summary.prose}</Text>
          <Text style={styles.sectionLabel}>KEYPOINTS</Text>
          {session.summary.keypoints?.map((kp: any, i: number) => (
            <View key={i} style={styles.kp}>
              <Text style={styles.kpHeading}>{kp.heading}</Text>
              {kp.bullets?.map((b: string, j: number) => (
                <Text key={j} style={styles.kpBullet}>• {b}</Text>
              ))}
            </View>
          ))}
          {session.summary.action_items?.length > 0 && (
            <>
              <Text style={styles.sectionLabel}>ACTION ITEMS</Text>
              {session.summary.action_items.map((a: string, i: number) => (
                <Text key={i} style={styles.actionItem}>☐ {a}</Text>
              ))}
            </>
          )}
        </>
      ) : (
        <Text style={styles.pending}>Summary generating…</Text>
      )}
      {session.cues?.length > 0 && (
        <>
          <Text style={styles.sectionLabel}>AI CUES ({session.cues.length})</Text>
          <View style={styles.cueGrid}>
            {session.cues.map((c: any) => (
              <CueChip key={c.cue_id} cue={c} />
            ))}
          </View>
        </>
      )}
    </View>
  );
}

function TranscriptTab({ session }: { session: any }) {
  return (
    <View>
      {(session.utterances ?? []).map((u: any, i: number) => (
        <View key={i} style={styles.utteranceRow}>
          <Text style={styles.utteranceTime}>{formatTime(u.t_start)}</Text>
          <Text style={styles.utteranceText}>{u.text}</Text>
        </View>
      ))}
    </View>
  );
}

function formatTime(secs: number): string {
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = Math.floor(secs % 60);
  return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#fff" },
  header: { flexDirection: "row", alignItems: "center", paddingHorizontal: 20, paddingTop: 56, paddingBottom: 16, gap: 12 },
  back: { fontSize: 17, color: "#007AFF" },
  title: { flex: 1, fontSize: 17, fontWeight: "600" },
  tabs: { flexDirection: "row", borderBottomWidth: StyleSheet.hairlineWidth, borderColor: "#E5E5E5" },
  tab: { flex: 1, paddingVertical: 12, alignItems: "center" },
  tabActive: { borderBottomWidth: 2, borderBottomColor: "#111" },
  tabText: { fontSize: 14, color: "#888" },
  tabTextActive: { color: "#111", fontWeight: "600" },
  content: { flex: 1, paddingHorizontal: 20 },
  live: { flex: 1, padding: 20, alignItems: "center" },
  timer: { fontSize: 48, fontVariant: ["tabular-nums"], marginTop: 20 },
  listeningLabel: { fontSize: 14, color: "#888", marginTop: 8 },
  liveCues: { width: "100%", marginTop: 24 },
  stopBtn: { marginTop: "auto", backgroundColor: "#E00", borderRadius: 14, paddingVertical: 16, paddingHorizontal: 40 },
  stopBtnText: { color: "#fff", fontSize: 17, fontWeight: "700" },
  summaryRoot: { paddingTop: 20 },
  sectionLabel: { fontSize: 11, fontWeight: "600", color: "#888", letterSpacing: 0.8, marginTop: 24, marginBottom: 8 },
  prose: { fontSize: 15, lineHeight: 22, color: "#222" },
  kp: { marginBottom: 12 },
  kpHeading: { fontSize: 15, fontWeight: "600", marginBottom: 4 },
  kpBullet: { fontSize: 14, color: "#444", paddingLeft: 8, lineHeight: 20 },
  actionItem: { fontSize: 14, color: "#222", paddingVertical: 4 },
  pending: { fontSize: 15, color: "#888", paddingTop: 40, textAlign: "center" },
  cueGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  utteranceRow: { paddingVertical: 8, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: "#F0F0F0" },
  utteranceTime: { fontSize: 11, fontFamily: "Menlo", color: "#888", marginBottom: 3 },
  utteranceText: { fontSize: 14, lineHeight: 20 },
});
