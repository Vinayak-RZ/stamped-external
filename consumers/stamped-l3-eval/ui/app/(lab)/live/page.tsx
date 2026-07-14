import { LiveClient } from "@/components/LiveClient";

export default function LivePage() {
  return (
    <>
      <h1>Live</h1>
      <p className="lede">
        Optional attach to a running stamped-l3-core lab export — same forensic table as offline
        artifacts.
      </p>
      <LiveClient />
    </>
  );
}
