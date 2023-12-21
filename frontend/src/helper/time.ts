export function formatSecondsToMinutes(seconds: number): string {
    let minutes = Math.floor(seconds / 60);
    let remainingSeconds = seconds % 60;
  
    // Pad the minutes and seconds with leading zeros if needed
    const strMinutes = String(minutes).padStart(2, '0');
    const strRemainingSeconds = String(remainingSeconds).padStart(2, '0');
  
    return `${strMinutes}:${strRemainingSeconds}`;
  }
  