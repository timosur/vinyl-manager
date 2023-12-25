export type KeySignature = {
    id: string;
    name: string;
    color: string;
    rotate: number;
};

export type MajorKeySignatures = KeySignature[];
export type MinorKeySignatures = KeySignature[];

export const majorKeySignatures: MajorKeySignatures = [
    // Major key signatures with RGB colors
    { id: '12B', name: 'E', color: 'rgb(72, 235, 235)', rotate: 0 },    // Cyan-like
    { id: '11B', name: 'A', color: 'rgb(71, 237, 202)', rotate: 165 },  // Between Cyan and Green
    { id: '10B', name: 'D', color: 'rgb(69, 238, 128)', rotate: 150 },  // Greenish
    { id: '9B', name: 'G', color: 'rgb(134, 242, 80)', rotate: 135 },   // Lime Green
    { id: '8B', name: 'C', color: 'rgb(199, 245, 32)', rotate: 120 },   // Yellow-Green
    { id: '7B', name: 'F', color: 'rgb(255, 247, 0)', rotate: 105 },    // Yellow
    { id: '6B', name: 'Bb', color: 'rgb(255, 195, 0)', rotate: 90 },    // Orange-Yellow
    { id: '5B', name: 'Eb', color: 'rgb(255, 144, 0)', rotate: 75 },    // Orange
    { id: '4B', name: 'Ab', color: 'rgb(255, 92, 0)', rotate: 60 },     // Dark Orange
    { id: '3B', name: 'Db', color: 'rgb(255, 41, 0)', rotate: 45 },     // Red-Orange
    { id: '2B', name: 'F#', color: 'rgb(255, 20, 0)', rotate: 30 },      // Red
    { id: '1B', name: 'B', color: 'rgb(255, 0, 0)', rotate: 15 },    // Purple
];

export const minorKeySignatures: MinorKeySignatures = [
    // Minor key signatures with RGB colors
    { id: '12A', name: 'C#m', color: 'rgb(86, 241, 218)', rotate: 180 }, // Aquamarine
    { id: '11A', name: 'G#m', color: 'rgb(86, 241, 218)', rotate: 195 }, // Aquamarine (same as 12A)
    { id: '10A', name: 'D#m', color: 'rgb(125, 242, 170)', rotate: 210 }, // Light Green
    { id: '9A', name: 'A#m', color: 'rgb(164, 243, 122)', rotate: 225 }, // Soft Lime
    { id: '8A', name: 'Fm', color: 'rgb(203, 244, 74)', rotate: 240 },   // Lime Yellow
    { id: '7A', name: 'Cm', color: 'rgb(241, 245, 26)', rotate: 255 },   // Lemon Yellow
    { id: '6A', name: 'Gm', color: 'rgb(255, 246, 0)', rotate: 270 },    // Yellow
    { id: '5A', name: 'Dm', color: 'rgb(255, 197, 0)', rotate: 285 },    // Yellow-Orange
    { id: '4A', name: 'Am', color: 'rgb(255, 148, 0)', rotate: 300 },    // Orange
    { id: '3A', name: 'Em', color: 'rgb(255, 99, 0)', rotate: 315 },     // Dark Orange
    { id: '2A', name: 'Bm', color: 'rgb(255, 50, 0)', rotate: 330 },     // Red-Orange
    { id: '1A', name: 'F#m', color: 'rgb(255, 0, 0)', rotate: 345 },    
]

