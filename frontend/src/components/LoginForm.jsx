import React, { useState } from "react"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log("Login attempt:", { email, password })
  }

  return (
    <div className="w-full max-w-md shadow-lg border border-border rounded-lg bg-card text-card-foreground">
      <div className="p-8">
        <div className="space-y-4 text-center pb-8">
          <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="text-2xl">🍽️</span>
          </div>
          <div className="space-y-2">
            <h1 className="text-3xl font-serif text-balance">Bienvenido</h1>
            <p className="text-base text-muted-foreground">
              Ingresa a tu cuenta para continuar
            </p>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Correo electrónico
            </label>
            <input
              id="email"
              type="email"
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full h-11 bg-input border border-border rounded px-3 text-foreground"
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="password" className="text-sm font-medium">
                Contraseña
              </label>
              <button type="button" className="text-sm text-primary hover:text-primary/80 transition-colors">
                ¿Olvidaste tu contraseña?
              </button>
            </div>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full h-11 bg-input border border-border rounded px-3 text-foreground"
            />
          </div>
          <button type="submit" className="w-full h-11 text-base font-medium bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors">
            Iniciar sesión
          </button>
        </form>
        <div className="mt-6 text-center">
          <p className="text-sm text-muted-foreground">
            ¿No tienes una cuenta?{" "}
            <button className="text-primary hover:text-primary/80 font-medium transition-colors">
              Regístrate aquí
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
