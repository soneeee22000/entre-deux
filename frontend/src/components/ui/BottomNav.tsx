import { NavLink } from "react-router-dom";
import { Home, FlaskConical, BookHeart, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/", icon: Home, label: "Accueil" },
  { to: "/analyses", icon: FlaskConical, label: "Analyses" },
  { to: "/journal", icon: BookHeart, label: "Journal" },
  { to: "/bilan", icon: FileText, label: "Bilan" },
] as const;

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-20 border-t border-border bg-background">
      <div className="flex items-center justify-around h-14">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex flex-col items-center justify-center gap-0.5 w-full h-full text-xs transition-colors",
                isActive ? "text-primary font-medium" : "text-muted-foreground",
              )
            }
          >
            <Icon size={22} />
            <span>{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
