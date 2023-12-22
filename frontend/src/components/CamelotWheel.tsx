import { majorKeySignatures, KeySignature, minorKeySignatures } from "@/models/Camelot";

export const CamelotWheelSegment = ({ type, keySignature, onSelectKey, index, totalKeys, isSelected }: { type: string, keySignature: KeySignature, onSelectKey: (key: string) => void, index: number, totalKeys: number, isSelected: boolean }) => {
  const degree = 360 / totalKeys;
  const rotation = degree * index;

  return (
    <div
      className={`key-wheel-segment-${type} ${isSelected ? 'selected' : ''}`}
      style={{
        backgroundColor: keySignature.color,
        transform: `rotate(-${rotation}deg)`,
      }}
      onClick={() => onSelectKey(keySignature.id)}
    >
      {keySignature.id}
    </div>
  );
};

export const CamelotWheel = ({ selectedKey, onSelectKey }: { selectedKey: string, onSelectKey: (key: string) => void }) => {
  return (<div className="key-wheel">
    {majorKeySignatures.map((key: KeySignature, index: number) => (
      <CamelotWheelSegment
        type="outer"
        key={key.name}
        keySignature={key}
        index={index}
        totalKeys={majorKeySignatures.length}
        onSelectKey={onSelectKey}
        isSelected={key.id === selectedKey}
      />
    ))}

    {minorKeySignatures.map((key: KeySignature, index: number) => (
      <CamelotWheelSegment
        type="inner"
        key={key.name}
        keySignature={key}
        index={index}
        totalKeys={minorKeySignatures.length}
        onSelectKey={onSelectKey}
        isSelected={key.id === selectedKey}
      />
    ))}

    <div className="key-wheel-center">
      {selectedKey}
    </div>
  </div>)
}