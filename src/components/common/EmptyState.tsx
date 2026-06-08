import { Inbox } from "lucide-react";

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="state-box">
      <Inbox size={24} />
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
}
