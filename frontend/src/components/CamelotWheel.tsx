import { camelotKeyColors } from "@/models/Camelot";

export const CamelotWheel = ({ keyName, onSelectKey, index, totalKeys }: { keyName: string, onSelectKey: (key: string) => void, index: number, totalKeys: number }) => {
    const degree = 360 / totalKeys;
    const rotation = degree * index;

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