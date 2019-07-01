export interface DiffContent {
    leftContent: string;
    rightContent: string;
  }
   
  export type DiffTableFormat = 'SideBySide' | 'LineByLine';
   
  export interface DiffResults {
    hasDiff: boolean;
    diffsCount: number;
    rowsWithDiff: {
      leftLineNumber?: number;
      rightLineNumber?: number;
      numDiffs: number;
    }[];
  }
  