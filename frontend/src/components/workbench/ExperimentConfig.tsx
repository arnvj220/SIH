import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { NumberInput } from "../ui/NumberInput";
import { Select } from "../ui/Select";
import { Slider } from "../ui/Slider";
import type { AttackDescription, ExperimentRunRequest } from "../../lib/types";

interface Props {
  attacks: AttackDescription[];
  value: ExperimentRunRequest;
  onChange: (v: ExperimentRunRequest) => void;
  onRun: () => void;
  running: boolean;
}

export function ExperimentConfig({
  attacks,
  value,
  onChange,
  onRun,
  running,
}: Props) {
  const selectedAttack = attacks.find((a) => a.name === value.attack_type);

  const update = <K extends keyof ExperimentRunRequest>(
    key: K,
    v: ExperimentRunRequest[K]
  ) => onChange({ ...value, [key]: v });

  const updateParam = (key: string, v: unknown) =>
    onChange({ ...value, parameters: { ...value.parameters, [key]: v } });

  return (
    <Card title="Experiment Configuration" subtitle="Configure the run" padded>
      <div className="space-y-4">
        <div>
          <label className="text-xs font-medium text-muted">Attack</label>
          <Select
            className="mt-1"
            value={value.attack_type}
            onChange={(e) =>
              onChange({
                ...value,
                attack_type: e.target.value,
                parameters: attacks.find((a) => a.name === e.target.value)
                  ?.default_parameters ?? {},
              })
            }
            options={attacks.map((a) => ({
              value: a.name,
              label: `${a.name} (${a.threat_type})`,
            }))}
          />
          {selectedAttack && (
            <p className="mt-1.5 text-xs text-muted">
              {selectedAttack.description}
            </p>
          )}
        </div>

        {selectedAttack && selectedAttack.modes.length > 0 && (
          <div>
            <label className="text-xs font-medium text-muted">Mode</label>
            <Select
              className="mt-1"
              value={String(value.parameters.mode ?? selectedAttack.modes[0])}
              onChange={(e) => updateParam("mode", e.target.value)}
              options={selectedAttack.modes.map((m) => ({
                value: m,
                label: m,
              }))}
            />
          </div>
        )}

        {typeof value.parameters.perturbation === "number" && (
          <Slider
            label="Perturbation"
            value={value.parameters.perturbation as number}
            min={0.01}
            max={1}
            step={0.01}
            onChange={(v) => updateParam("perturbation", v)}
          />
        )}

        {typeof value.parameters.modified_fraction === "number" && (
          <Slider
            label="Modified fraction"
            value={value.parameters.modified_fraction as number}
            min={0.01}
            max={1}
            step={0.01}
            onChange={(v) => updateParam("modified_fraction", v)}
          />
        )}

        <div className="grid grid-cols-2 gap-3">
          <NumberInput
            label="Targets"
            value={value.n_targets}
            min={1}
            max={5000}
            onChange={(v) => update("n_targets", v)}
          />
          <NumberInput
            label="Rounds"
            value={value.rounds}
            min={1}
            max={100000}
            onChange={(v) => update("rounds", v)}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <NumberInput
            label="Seed"
            value={value.seed}
            onChange={(v) => update("seed", v)}
          />
          <NumberInput
            label="Noise (0-0.5)"
            value={value.natural_error_rate}
            min={0}
            max={0.49}
            step={0.005}
            onChange={(v) => update("natural_error_rate", v)}
          />
        </div>

        <Button
          onClick={onRun}
          disabled={running}
          className="w-full"
          variant="primary"
        >
          {running ? "Running…" : "▶ Run Experiment"}
        </Button>

        <div className="border-t border-border pt-3 text-[11px] text-muted">
          <div className="font-mono">
            seed={value.seed} · targets={value.n_targets} · rounds={value.rounds}
          </div>
          <div className="mt-1">
            Reproducible: same inputs → same result.
          </div>
        </div>
      </div>
    </Card>
  );
}