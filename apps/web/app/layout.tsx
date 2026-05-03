import "./globals.css";
import type { ReactNode } from "react";

import { FilterProvider } from "../components/FilterProvider";
import NavBar from "../components/NavBar";
import Providers from "../components/Providers";

export const metadata = {
  title: "Water Polo Champions League",
  description: "Analytics dashboard"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <Providers>
            <FilterProvider>
              <NavBar />
              <main className="mx-auto max-w-[1280px] px-4 pb-16 pt-6 sm:px-6 sm:pt-8">{children}</main>
            </FilterProvider>
          </Providers>
        </div>
      </body>
    </html>
  );
}
