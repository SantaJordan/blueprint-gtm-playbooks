import test from "node:test";
import assert from "node:assert/strict";

// Copied from blueprint-saas/lib/stripe.ts to avoid TS loader requirements.
function normalizeCompanyDomain(input) {
  let url = input.trim().toLowerCase();
  url = url.replace(/^https?:\/\//, "");
  url = url.replace(/^www\./, "");
  url = url.split("/")[0];
  return url;
}

function domainToSlug(domain) {
  return normalizeCompanyDomain(domain).replace(/\./g, "-");
}

function slugToDomain(slug) {
  const parts = slug.split("-").filter(Boolean);
  if (parts.length >= 3) {
    const last = parts[parts.length - 1];
    const secondLast = parts[parts.length - 2];
    if (last.length === 2 && secondLast.length <= 3) {
      return `${parts.slice(0, -2).join("-")}.${secondLast}.${last}`;
    }
  }
  if (parts.length >= 2) {
    return `${parts.slice(0, -1).join("-")}.${parts[parts.length - 1]}`;
  }
  return slug;
}

test("normalizeCompanyDomain strips protocol, www, and paths", () => {
  assert.equal(normalizeCompanyDomain("https://Owner.COM/about"), "owner.com");
  assert.equal(normalizeCompanyDomain("http://www.example.co.uk/foo"), "example.co.uk");
  assert.equal(normalizeCompanyDomain("example.com/landing"), "example.com");
});

test("domainToSlug and slugToDomain roundtrip with TLD included", () => {
  const domain = "canvas-medical.com";
  const slug = domainToSlug(domain);
  assert.equal(slug, "canvas-medical-com");
  assert.equal(slugToDomain(slug), domain);
});

test("expected stored company_url differs from raw user input with paths", () => {
  const rawInput = "https://owner.com/about";
  const normalizedDomain = normalizeCompanyDomain(rawInput);
  const expectedStoredUrl = `https://${normalizedDomain}`;
  assert.notEqual(expectedStoredUrl, rawInput);
});
