"use client";

import { useEffect } from "react";

/** Браузер не всегда доскролливает до #contact после клиентского перехода. */
export function HashScroll() {
  useEffect(() => {
    const id = window.location.hash.replace("#", "");
    if (!id) return;
    document.getElementById(id)?.scrollIntoView();
  }, []);

  return null;
}
