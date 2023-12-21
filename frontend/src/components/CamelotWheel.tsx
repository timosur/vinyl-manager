import { camelotKeyColors } from "@/models/Camelot";

export const CamelotWheel = ({ keyName, onSelectKey, index, totalKeys, isSelected }: { keyName: string, onSelectKey: (key: string) => void, index: number, totalKeys: number, isSelected: boolean }) => {
    const degree = 360 / totalKeys;
    const rotation = degree * index;

    const segmentColor = isSelected ? camelotKeyColors[keyName] : '#ccc'; // Grau für nicht ausgewählte

    return (
      <div
      className="key-wheel-segment"
      style={{
        backgroundColor: camelotKeyColors[keyName],
        transform: `rotate(-${rotation}deg)`,
      }}
      onClick={() => onSelectKey(keyName)}
    >
      {keyName}
    </div>
    );
  };