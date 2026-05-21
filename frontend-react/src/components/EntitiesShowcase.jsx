import './EntitiesShowcase.css';

const TYPE_COLORS = {
  Diagnosis:  { bg: 'hsla(258,70%,60%,0.15)', border: 'hsla(258,70%,60%,0.35)', color: 'hsl(258,80%,75%)' },
  Procedure:  { bg: 'hsla(210,80%,55%,0.15)', border: 'hsla(210,80%,55%,0.35)', color: 'hsl(210,90%,70%)' },
  Medication: { bg: 'hsla(175,65%,45%,0.15)', border: 'hsla(175,65%,45%,0.35)', color: 'hsl(175,70%,58%)' },
  Symptom:    { bg: 'hsla(42,85%,55%,0.12)',  border: 'hsla(42,85%,55%,0.3)',   color: 'hsl(42,90%,65%)'  },
  Finding:    { bg: 'hsla(345,75%,55%,0.12)', border: 'hsla(345,75%,55%,0.3)',  color: 'hsl(345,80%,70%)' },
  default:    { bg: 'hsla(220,20%,50%,0.12)', border: 'hsla(220,20%,50%,0.25)', color: 'var(--text-secondary)' },
};

export default function EntitiesShowcase({ entities = [] }) {
  if (!entities.length) return null;

  return (
    <div className="entities-wrap">
      {entities.map((ent, i) => {
        const style = TYPE_COLORS[ent.entity_type] || TYPE_COLORS.default;
        return (
          <span
            key={i}
            className="entity-chip"
            style={{
              background: style.bg,
              border: `1px solid ${style.border}`,
              color: style.color,
            }}
            title={ent.entity_type}
          >
            <span className="entity-dot" style={{ background: style.color }} />
            {ent.entity_text}
          </span>
        );
      })}
    </div>
  );
}
