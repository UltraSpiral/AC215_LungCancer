import { useState, type ReactNode } from 'react';
import {
  Button,
  Chip,
  GlassCard,
  ProgressBar,
  SegmentedNav,
  Slider,
  StatNumber,
  Textarea,
  Toggle,
} from '../components/ui';
import styles from './KitchenSink.module.css';
import { PanelStates } from './PanelStates';

const SWATCHES = [
  'page',
  'ink',
  'text-body',
  'text-muted',
  'text-secondary',
  'text-tertiary',
  'text-disabled',
  'text-faint',
  'accent',
  'accent-outline',
  'accent-10',
  'warning',
  'warning-bg',
  'warning-text',
  'warning-heading',
  'slide-pane',
];

function Section({ title, figma, children }: { title: string; figma: string; children: ReactNode }) {
  return (
    <GlassCard className={styles.section}>
      <header className={styles.sectionHeader}>
        <h2>{title}</h2>
        <span className={styles.figma}>{figma}</span>
      </header>
      <div className={styles.row}>{children}</div>
    </GlassCard>
  );
}

/** /kitchen-sink — every primitive rendered against its Figma reference. */
export function KitchenSink() {
  const [tab, setTab] = useState('review');
  const [heatmap, setHeatmap] = useState(true);
  const [qc, setQc] = useState(false);
  const [opacity, setOpacity] = useState(60);

  return (
    <main className={styles.page}>
      <h1 className={styles.title}>Kitchen sink</h1>
      <p className={styles.lede}>
        Primitives rendered from src/styles/tokens.css, labelled with their Figma references.
      </p>

      <Section title="Colour tokens" figma="tokens.css · --color-*">
        {SWATCHES.map((name) => (
          <div key={name} className={styles.swatch}>
            <span className={styles.chipColor} style={{ background: `var(--color-${name})` }} />
            <code>{name}</code>
          </div>
        ))}
      </Section>

      <Section title="Typography" figma="Geist / Geist Mono">
        <div className={styles.stack}>
          <span style={{ font: '500 26px/34px var(--font-sans)', letterSpacing: 'var(--tracking-26)' }}>
            Medium 26 · Pathology report
          </span>
          <span style={{ font: '500 22px/26.4px var(--font-sans)', letterSpacing: 'var(--tracking-22)' }}>
            Medium 22 · Most consistent with
          </span>
          <span style={{ font: '500 20px/26px var(--font-numeric)', letterSpacing: 'var(--tracking-case-id)' }}>
            Instrument Sans Medium 20 · LH-2026-0417
          </span>
          <span style={{ font: '600 14px/18px var(--font-sans)' }}>SemiBold 14 · Section title</span>
          <span style={{ font: '600 13px/17px var(--font-sans)' }}>SemiBold 13 · AI analysis</span>
          <span style={{ font: '400 13px/17px var(--font-sans)' }}>Regular 13 · UI text</span>
          <span style={{ font: '400 12px/16px var(--font-sans)', color: 'var(--color-text-secondary)' }}>
            Regular 12 · Caption
          </span>
          <span style={{ font: '400 12px/16px var(--font-numeric)', color: 'var(--color-text-secondary)' }}>
            Instrument Sans 12 · 10×
          </span>
        </div>
      </Section>

      <Section title="SegmentedNav" figma="Overlay+Border+Shadow · 267×43">
        <SegmentedNav
          aria-label="Example"
          items={[
            { id: 'queue', label: 'Queue · 11' },
            { id: 'review', label: 'Review' },
            { id: 'report', label: 'Report' },
          ]}
          activeId={tab}
          onSelect={setTab}
        />
      </Section>

      <Section title="Buttons" figma="Agree 160×44 · Disagree 160×46 · Submit 38 · Fit 35">
        <Button>Agree</Button>
        <Button variant="secondary">Disagree</Button>
        <Button size="md">Submit</Button>
        <Button variant="ghost" size="md">
          Cancel
        </Button>
        <Button variant="glass" size="sm">
          Fit
        </Button>
        <Button disabled>Disabled</Button>
      </Section>

      <Section title="Chips & tags" figma="Urgent · Confident · Declined · AI Assist">
        <Chip tone="warning">Urgent · 48 h</Chip>
        <Chip tone="accent" dot>
          Confident
        </Chip>
        <Chip tone="dark" dot>
          Declined to predict
        </Chip>
        <Chip tone="neutral">Routine · 5 days</Chip>
        <Chip tone="accent" size="sm">
          AI Assist
        </Chip>
        <Chip tone="dark" size="sm">
          Pathologist-written
        </Chip>
        <Chip tone="glass" size="xs">
          Pathologist
        </Chip>
        <Chip tone="soft" size="xs">
          Hide ›
        </Chip>
      </Section>

      <Section title="Toggles & slider" figma="Layer toggles 30×16 · Opacity 120">
        <Toggle label="Heatmap" checked={heatmap} onChange={setHeatmap} />
        <Toggle label="QC marks" checked={qc} onChange={setQc} />
        <Toggle label="Tumor outline" checked={false} onChange={() => {}} disabled note="(low confidence)" />
        <Slider label="Opacity" value={opacity} onChange={setOpacity} />
      </Section>

      <Section title="Stat numbers" figma="Light 52 + Light 24 suffix">
        <StatNumber value={91} suffix="%" label="Confidence" />
        <StatNumber value={41} suffix="%" label="Confidence, needs 70%" muted />
        <StatNumber value={null} label="Tumor area not estimated" />
        <StatNumber value="1,862" label="Tiles analysed" />
      </Section>

      <Section title="Progress" figma="Probability bar · 4px on ink @8%">
        <div className={styles.stack} style={{ width: 320 }}>
          <ProgressBar value={0.62} label="Determinate" />
          <ProgressBar value={null} label="Indeterminate" />
        </div>
      </Section>

      <Section title="Textarea" figma="Textarea · radius 12 · focus #2F66F0@45%">
        <div style={{ width: 400 }}>
          <Textarea placeholder="e.g. Squamous cell carcinoma, non-keratinizing" />
        </div>
      </Section>

      <Section title="Glass surfaces" figma="Card white@72% · Modal white@94%">
        <GlassCard className={styles.demoCard}>Card</GlassCard>
        <GlassCard variant="modal" className={styles.demoCard}>
          Modal
        </GlassCard>
      </Section>

      <h2 className={styles.title}>Analysis panel states</h2>
      <PanelStates />
    </main>
  );
}
