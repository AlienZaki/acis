/**
 * Settings screen.
 *
 * Sections:
 *  1. Microphone source  (Glasses / Phone / Laptop)
 *  2. Audio output       (Meta Glasses / Phone Speaker / Silent)
 *  3. Cues               (Speak Cues toggle, Auto Speak toggle, Cue Verbosity)
 *  4. Transcript         (Live Transcript on Phone toggle)
 *  5. Connection         (Backend URL, ASR model)
 *  6. Privacy            (Processed by Mistral AI link)
 */

import React, { useCallback } from "react";
import {
  Linking,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useSettingsStore } from "../store/settings";

export function Settings() {
  const settings = useSettingsStore((s) => s.settings);
  const update = useSettingsStore((s) => s.update);

  return (
    <ScrollView style={styles.root} contentContainerStyle={{ paddingBottom: 60 }}>
      <Text style={styles.screenTitle}>Settings</Text>

      {/* Microphone source */}
      <Section title="Microphone">
        <RadioRow
          label="Glasses mic"
          description="5-mic array. Uses HFP — audio quality drops to 8 kHz mono."
          selected={settings.micSource === "glasses"}
          onSelect={() => update({ micSource: "glasses" })}
        />
        <RadioRow
          label="Phone mic"
          description="Captures ambient room audio. Keeps A2DP for high-quality TTS."
          selected={settings.micSource === "phone"}
          onSelect={() => update({ micSource: "phone" })}
        />
        <RadioRow
          label="Laptop mic"
          description="CLI / desktop mode."
          selected={settings.micSource === "laptop"}
          onSelect={() => update({ micSource: "laptop" })}
        />
      </Section>

      {/* Audio output */}
      <Section title="Audio Output">
        <RadioRow
          label="Meta Glasses"
          description="Speak cues through open-ear speakers via A2DP."
          selected={settings.audioOutput === "glasses"}
          onSelect={() => update({ audioOutput: "glasses" })}
        />
        <RadioRow
          label="Phone Speaker"
          description="Fall back to phone when glasses are not connected."
          selected={settings.audioOutput === "phone"}
          onSelect={() => update({ audioOutput: "phone" })}
        />
        <RadioRow
          label="Silent (app only)"
          description="No audio. Cues visible in app only."
          selected={settings.audioOutput === "silent"}
          onSelect={() => update({ audioOutput: "silent" })}
        />
      </Section>

      {/* Cues */}
      <Section title="Cues">
        <ToggleRow
          label="Speak Cues"
          description="Play audio cues through the output device."
          value={settings.speakCues}
          onValueChange={(v) => update({ speakCues: v })}
        />
        <ToggleRow
          label="Auto Speak"
          description="Speak cues immediately as they arrive. Off = tap glasses frame."
          value={settings.autoSpeak}
          onValueChange={(v) => update({ autoSpeak: v })}
        />
        <NavRow
          label="Cue Verbosity"
          value={settings.cueVerbosity === "brief" ? "Brief" : "Full"}
          onPress={() => {
            update({ cueVerbosity: settings.cueVerbosity === "brief" ? "full" : "brief" });
          }}
        />
      </Section>

      {/* Transcript */}
      <Section title="Transcript">
        <ToggleRow
          label="Live Transcript on Phone"
          description="Show real-time transcript on phone screen during session."
          value={settings.liveTranscriptOnPhone}
          onValueChange={(v) => update({ liveTranscriptOnPhone: v })}
        />
      </Section>

      {/* Privacy */}
      <Section title="Privacy">
        <TouchableOpacity
          style={styles.privacyRow}
          onPress={() => Linking.openURL("https://mistral.ai/terms/#data-processing")}
        >
          <Text style={styles.privacyText}>Audio and transcript processed by Mistral AI</Text>
          <Text style={styles.privacyLink}>↗ Data Processing Agreement</Text>
        </TouchableOpacity>
      </Section>
    </ScrollView>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title.toUpperCase()}</Text>
      <View style={styles.sectionBody}>{children}</View>
    </View>
  );
}

function RadioRow({ label, description, selected, onSelect }: { label: string; description?: string; selected: boolean; onSelect: () => void }) {
  return (
    <TouchableOpacity style={styles.row} onPress={onSelect}>
      <View style={styles.radioOuter}>{selected && <View style={styles.radioInner} />}</View>
      <View style={styles.rowText}>
        <Text style={styles.rowLabel}>{label}</Text>
        {description && <Text style={styles.rowDesc}>{description}</Text>}
      </View>
    </TouchableOpacity>
  );
}

function ToggleRow({ label, description, value, onValueChange }: { label: string; description?: string; value: boolean; onValueChange: (v: boolean) => void }) {
  return (
    <View style={styles.row}>
      <View style={styles.rowText}>
        <Text style={styles.rowLabel}>{label}</Text>
        {description && <Text style={styles.rowDesc}>{description}</Text>}
      </View>
      <Switch value={value} onValueChange={onValueChange} />
    </View>
  );
}

function NavRow({ label, value, onPress }: { label: string; value: string; onPress: () => void }) {
  return (
    <TouchableOpacity style={styles.row} onPress={onPress}>
      <Text style={[styles.rowLabel, { flex: 1 }]}>{label}</Text>
      <Text style={styles.navValue}>{value}</Text>
      <Text style={styles.chevron}>›</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#F2F2F7" },
  screenTitle: { fontSize: 28, fontWeight: "700", paddingHorizontal: 20, paddingTop: 56, paddingBottom: 20 },
  section: { marginBottom: 24 },
  sectionTitle: { fontSize: 12, fontWeight: "600", color: "#6E6E73", paddingHorizontal: 20, paddingBottom: 8, letterSpacing: 0.5 },
  sectionBody: { backgroundColor: "#fff", borderRadius: 12, marginHorizontal: 16, overflow: "hidden" },
  row: { flexDirection: "row", alignItems: "center", paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: "#E5E5EA" },
  rowText: { flex: 1, marginLeft: 12 },
  rowLabel: { fontSize: 15 },
  rowDesc: { fontSize: 12, color: "#888", marginTop: 2, lineHeight: 16 },
  radioOuter: { width: 20, height: 20, borderRadius: 10, borderWidth: 2, borderColor: "#007AFF", alignItems: "center", justifyContent: "center" },
  radioInner: { width: 10, height: 10, borderRadius: 5, backgroundColor: "#007AFF" },
  navValue: { fontSize: 15, color: "#888" },
  chevron: { fontSize: 18, color: "#C7C7CC", marginLeft: 6 },
  privacyRow: { padding: 16 },
  privacyText: { fontSize: 14, color: "#444" },
  privacyLink: { fontSize: 13, color: "#007AFF", marginTop: 4 },
});
