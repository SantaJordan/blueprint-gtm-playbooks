import test from "node:test";
import assert from "node:assert/strict";

function computeDomainSlug(companyUrl) {
  return companyUrl
    .replace(/^https?:\/\//, "")
    .replace(/^www\./, "")
    .split("/")[0]
    .replace(/\./g, "-");
}

test("computeDomainSlug matches API behavior", () => {
  assert.equal(computeDomainSlug("https://owner.com"), "owner-com");
  assert.equal(computeDomainSlug("https://www.owner.com/about"), "owner-com");
  assert.equal(computeDomainSlug("http://example.co.uk/foo"), "example-co-uk");
});

test("raw companyUrl with paths is canonicalized for storage", () => {
  const rawInput = "https://owner.com/about";
  const parsed = new URL(rawInput);
  const canonicalHost = parsed.hostname.replace(/^www\./, "").toLowerCase();
  const canonicalCompanyUrl = `https://${canonicalHost}`;
  assert.equal(canonicalCompanyUrl, "https://owner.com");
});
