import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Master Scraper',
  description: 'Dashboard para ejecutar scrapers y generar reportes',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}

