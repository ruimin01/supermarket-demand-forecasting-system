import React, { useState } from "react";
import { createStaffAccount } from "../../services/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function CreateStaffAccountForm() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    is_active: true,
  });

  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [errorText, setErrorText] = useState("");

  async function handleSubmit() {
    try {
      setSubmitting(true);
      setMessage("");
      setErrorText("");

      const result = await createStaffAccount(form);

      setMessage("Staff account created successfully.");
      setForm({
        username: "",
        email: "",
        password: "",
        is_active: true,
      });
    } catch (error) {
      setErrorText(error.message || "Failed to create account");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card className="rounded-3xl border-0 shadow-md bg-white/85">
      <CardHeader>
        <CardTitle>Create Staff Account</CardTitle>
        <CardDescription>
          Administrators can create ordinary staff accounts here. Public registration is not enabled.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Username</label>
            <Input
              placeholder="Enter username"
              className="rounded-2xl h-11"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Email</label>
            <Input
              placeholder="Enter email"
              className="rounded-2xl h-11"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-medium">Initial Password</label>
            <Input
              type="password"
              placeholder="Enter initial password"
              className="rounded-2xl h-11"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
        </div>

        <label className="flex items-center gap-3 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />
          Account is active
        </label>

        {message && (
          <div className="rounded-2xl border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {message}
          </div>
        )}

        {errorText && (
          <div className="rounded-2xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorText}
          </div>
        )}

        <Button className="rounded-2xl" onClick={handleSubmit} disabled={submitting}>
          {submitting ? "Creating..." : "Create Staff Account"}
        </Button>
      </CardContent>
    </Card>
  );
}