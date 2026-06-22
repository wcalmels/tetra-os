import { useState } from "react";

const FILES = [
  {
    id: "f1",
    filename: "tetra_os_improved.py",
    dest: "tetra-os\\",
    description: "Sistema base — 5 algoritmos, consciencia, benchmarks",
    size: "~800 líneas",
    artifactId: "tetra_os_improved",
    color: "#EEEDFE",
    tc: "#3C3489",
    icon: "⚙️"
  },
  {
    id: "f2",
    filename: "tetra_science_module.py",
    dest: "tetra-os\\",
    description: "Módulos científicos — Drug design, Materials, Energy",
    size: "~1000 líneas",
    artifactId: "tetra_science_module",
    color: "#E1F5EE",
    tc: "#0F6E56",
    icon: "🔬"
  },
  {
    id: "f3",
    filename: "tetra_meta_discovery.py",
    dest: "tetra-os\\",
    description: "Meta-discovery — Law discovery, Algorithm generation",
    size: "~1200 líneas",
    artifactId: "tetra_meta_discovery",
    color: "#FBEAF0",
    tc: "#993556",
    icon: "🧠"
  },
  {
    id: "f4",
    filename: "tetra_complete_package.py",
    dest: "tetra-os\\",
    description: "CLI avanzado, instalador, integración completa",
    size: "~1500 líneas",
    artifactId: "tetra_complete_package",
    color: "#FAEEDA",
    tc: "#854F0B",
    icon: "📦"
  },
  {
    id: "f5",
    filename: "tetra_web_dashboard.py",
    dest: "tetra-os\\",
    description: "Dashboard web interactivo con Flask",
    size: "~800 líneas",
    artifactId: "tetra_web_dashboard",
    color: "#E6F1FB",
    tc: "#185FA5",
    icon: "🌐"
  },
  {
    id: "f6",
    filename: "tetra_extended_experiments.py",
    dest: "tetra-os\\experiments\\",
    description: "8 experimentos extendidos para el paper",
    size: "~700 líneas",
    artifactId: "tetra_extended_experiments",
    color: "#EAF3DE",
    tc: "#3B6D11",
    icon: "🧪"
  },
  {
    id: "f7",
    filename: "tetra_first_test.py",
    dest: "tetra-os\\tests\\",
    description: "Suite de 7 tests — 100% passing",
    size: "~300 líneas",
    artifactId: "tetra_first_test",
    color: "#EEEDFE",
    tc: "#3C3489",
    icon: "✅"
  }
];

const STEPS = [
  {
    n: "A",
    title: "Abrir el artifact en Claude",
    detail: "En el panel de la izquierda (o arriba en esta conversación), cada artifact tiene un botón para verlo."
  },
  {
    n: "B",
    title: "Copiar el contenido completo",
    detail: 'Clic en el botón "Copy" (icono de copiar) en la esquina superior derecha del bloque de código.'
  },
  {
    n: "C",
    title: "Crear el archivo en tu PC",
    detail: "Abre el Bloc de notas (o VS Code), pega el contenido y guarda con el nombre exacto indicado."
  },
  {
    n: "D",
    title: "Guardar en la carpeta correcta",
    detail: 'Usa la columna "Destino" de la tabla. La mayoría va directo en tetra-os\\'
  }
];

export default function App() {
  const [checked, setChecked] = useState({});
  const [activeMethod, setActiveMethod] = useState("manual");

  const toggle = (id) => setChecked(prev => ({ ...prev, [id]: !prev[id] }));
  const doneCount = Object.values(checked).filter(Boolean).length;

  const psScript = FILES.map(f =>
    `# ${f.filename}\n# Pega el contenido del artifact "${f.artifactId}" y guarda en:\n# ${f.dest}${f.filename}\n`
  ).join("\n");

  return (
    <div style={{ fontFamily: "var(--font-sans)", padding: "0 0 16px" }}>

      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 18, fontWeight: 500, margin: "0 0 6px" }}>
          Archivos Python de TETRA OS
        </h1>
        <p style={{ fontSize: 13, color: "var(--color-text-secondary)", margin: 0 }}>
          7 archivos · todos en esta conversación · listos para copiar
        </p>
      </div>

      {/* Progress bar */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between",
          marginBottom: 6, fontSize: 12, color: "var(--color-text-secondary)" }}>
          <span>Progreso</span>
          <span style={{ fontWeight: 500 }}>{doneCount} / {FILES.length} copiados</span>
        </div>
        <div style={{ background: "var(--color-background-secondary)",
          height: 8, borderRadius: 999, overflow: "hidden" }}>
          <div style={{ background: "#7F77DD", height: "100%", borderRadius: 999,
            width: `${(doneCount / FILES.length) * 100}%`,
            transition: "width 0.3s" }} />
        </div>
      </div>

      {/* Method tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {[
          { id: "manual", label: "📋 Método manual" },
          { id: "howto",  label: "❓ Cómo copiar" },
        ].map(t => (
          <button key={t.id} onClick={() => setActiveMethod(t.id)}
            style={{ fontSize: 12, padding: "6px 14px", borderRadius: "var(--border-radius-md)",
              border: "0.5px solid var(--color-border-tertiary)", cursor: "pointer",
              background: activeMethod === t.id ? "#EEEDFE" : "var(--color-background-secondary)",
              color: activeMethod === t.id ? "#3C3489" : "var(--color-text-secondary)",
              fontWeight: activeMethod === t.id ? 500 : 400 }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Manual method */}
      {activeMethod === "manual" && (
        <div>
          <p style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 12 }}>
            Marca cada archivo a medida que lo copies. Haz clic en el nombre del artifact para ir directo a él.
          </p>

          {FILES.map(f => (
            <div key={f.id}
              style={{ display: "flex", alignItems: "flex-start", gap: 12,
                padding: "12px 14px", marginBottom: 8,
                background: checked[f.id] ? "#E1F5EE" : "var(--color-background-primary)",
                border: `0.5px solid ${checked[f.id] ? "#9FE1CB" : "var(--color-border-tertiary)"}`,
                borderRadius: "var(--border-radius-lg)", transition: "all 0.2s" }}>

              {/* Checkbox */}
              <input type="checkbox" checked={!!checked[f.id]}
                onChange={() => toggle(f.id)}
                style={{ width: 16, height: 16, marginTop: 2, cursor: "pointer", flexShrink: 0 }} />

              {/* Icon + info */}
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 14 }}>{f.icon}</span>
                  <code style={{ fontSize: 13, fontWeight: 500,
                    color: checked[f.id] ? "#0F6E56" : "var(--color-text-primary)" }}>
                    {f.filename}
                  </code>
                  <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 999,
                    background: f.color, color: f.tc }}>
                    {f.size}
                  </span>
                </div>
                <p style={{ fontSize: 12, color: "var(--color-text-secondary)",
                  margin: "4px 0 6px" }}>
                  {f.description}
                </p>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ fontSize: 11, color: "var(--color-text-tertiary)" }}>
                    Guardar en:
                  </span>
                  <code style={{ fontSize: 11,
                    background: "var(--color-background-secondary)",
                    padding: "2px 8px", borderRadius: 4,
                    color: "var(--color-text-secondary)" }}>
                    {f.dest}{f.filename}
                  </code>
                </div>
              </div>

              {/* Status */}
              <div style={{ fontSize: 18, flexShrink: 0 }}>
                {checked[f.id] ? "✅" : "⬜"}
              </div>
            </div>
          ))}

          {doneCount === FILES.length && (
            <div style={{ marginTop: 12, padding: "14px 16px",
              background: "#E1F5EE", border: "0.5px solid #9FE1CB",
              borderRadius: "var(--border-radius-lg)" }}>
              <p style={{ fontSize: 14, fontWeight: 500, color: "#0F6E56", margin: "0 0 4px" }}>
                🎉 ¡Todos los archivos copiados!
              </p>
              <p style={{ fontSize: 12, color: "#0F6E56", margin: 0 }}>
                Siguiente paso: ejecutar <code>python tetra_first_test.py</code> para verificar.
              </p>
            </div>
          )}
        </div>
      )}

      {/* How to copy */}
      {activeMethod === "howto" && (
        <div>
          <p style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 14 }}>
            Para cada archivo, sigue estos 4 pasos:
          </p>

          {STEPS.map((s, i) => (
            <div key={s.n} style={{ display: "flex", gap: 12, marginBottom: 14 }}>
              <div style={{ width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
                background: "#EEEDFE", color: "#3C3489",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 13, fontWeight: 500 }}>
                {s.n}
              </div>
              <div>
                <p style={{ fontSize: 13, fontWeight: 500, margin: "0 0 4px",
                  color: "var(--color-text-primary)" }}>{s.title}</p>
                <p style={{ fontSize: 12, color: "var(--color-text-secondary)",
                  margin: 0, lineHeight: 1.6 }}>{s.detail}</p>
              </div>
            </div>
          ))}

          <div style={{ background: "var(--color-background-secondary)",
            border: "0.5px solid var(--color-border-tertiary)",
            borderRadius: "var(--border-radius-lg)", padding: "14px 16px",
            marginTop: 8 }}>
            <p style={{ fontSize: 13, fontWeight: 500, margin: "0 0 8px" }}>
              💡 Tip — Usa VS Code para más comodidad
            </p>
            <p style={{ fontSize: 12, color: "var(--color-text-secondary)",
              margin: "0 0 10px", lineHeight: 1.6 }}>
              1. Abre la carpeta <code>tetra-os</code> en VS Code<br/>
              2. Ctrl+N → nuevo archivo<br/>
              3. Pega el contenido<br/>
              4. Ctrl+Shift+S → guardar con el nombre exacto
            </p>
            <p style={{ fontSize: 12, color: "var(--color-text-secondary)", margin: 0 }}>
              VS Code: <strong>https://code.visualstudio.com</strong> (gratis)
            </p>
          </div>

          <div style={{ marginTop: 14, padding: "12px 14px",
            background: "#FAEEDA", border: "0.5px solid #FAC775",
            borderRadius: "var(--border-radius-lg)" }}>
            <p style={{ fontSize: 12, fontWeight: 500, color: "#854F0B", margin: "0 0 4px" }}>
              ⚠️ Nombre exacto del archivo
            </p>
            <p style={{ fontSize: 12, color: "#854F0B", margin: 0 }}>
              El nombre debe ser exactamente igual al indicado, incluyendo guiones bajos.
              Python es sensible a mayúsculas y al nombre del módulo.
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ marginTop: 20, paddingTop: 14,
        borderTop: "0.5px solid var(--color-border-tertiary)",
        fontSize: 12, color: "var(--color-text-tertiary)" }}>
        Todos los artifacts están disponibles en esta conversación de Claude.
        Desplázate hacia arriba para encontrar cada uno por su título.
      </div>
    </div>
  );
}