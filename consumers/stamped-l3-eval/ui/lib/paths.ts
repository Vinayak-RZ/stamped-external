import path from "path";

export function evalRoot(): string {
  return path.resolve(process.cwd(), "..");
}

export function corpusPath(): string {
  return path.join(evalRoot(), "corpus", "v0", "windows.json");
}

export function goldenDir(): string {
  return path.join(evalRoot(), "artifacts", "golden");
}
