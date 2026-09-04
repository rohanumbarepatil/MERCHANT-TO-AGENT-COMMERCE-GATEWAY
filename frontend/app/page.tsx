"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(data.status);
      })
      .catch(() => {
        setBackendStatus("Backend unavailable");
      });
  }, []);

  return (
    <main>
      <h1>Merchant-to-Agent Commerce Gateway</h1>
      <p>AI-powered, permissioned commerce infrastructure.</p>

      <p>Backend Status: {backendStatus}</p>
    </main>
  );
}