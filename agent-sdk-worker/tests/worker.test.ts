import test from "node:test";
import assert from "node:assert/strict";

import { __test__ } from "../src/worker.ts";

test("extractCompanySlug includes TLD and normalizes", () => {
  assert.equal(__test__.extractCompanySlug("https://owner.com"), "owner-com");
  assert.equal(
    __test__.extractCompanySlug("https://www.canvas-medical.com/about"),
    "canvas-medical-com"
  );
  assert.equal(
    __test__.extractCompanySlug("http://example.co.uk/path"),
    "example-co-uk"
  );
});

test("extractOldCompanySlug strips common TLDs only", () => {
  assert.equal(__test__.extractOldCompanySlug("https://owner.com"), "owner");
  assert.equal(
    __test__.extractOldCompanySlug("https://www.canvas-medical.com"),
    "canvas-medical"
  );
  // Multi-part TLDs are not stripped by current implementation.
  assert.equal(
    __test__.extractOldCompanySlug("https://example.co.uk"),
    "example-co-uk"
  );
});

test("new vs old slug mismatch for .com domains", () => {
  const url = "https://owner.com";
  const newSlug = __test__.extractCompanySlug(url);
  const oldSlug = __test__.extractOldCompanySlug(url);
  assert.notEqual(newSlug, oldSlug);
});

test("extractPlaybookUrl prioritizes github pages then local paths", () => {
  const githubText =
    "Playbook ready: https://santajordan.github.io/blueprint-gtm-playbooks/blueprint-gtm-playbook-owner.html";
  assert.equal(
    __test__.extractPlaybookUrl(githubText),
    "https://santajordan.github.io/blueprint-gtm-playbooks/blueprint-gtm-playbook-owner.html"
  );

  const localText =
    "PLAYBOOK_PATH: playbooks/blueprint-gtm-playbook-owner.html";
  assert.equal(
    __test__.extractPlaybookUrl(localText),
    "https://santajordan.github.io/blueprint-gtm-playbooks/blueprint-gtm-playbook-owner.html"
  );
});

test("extractPlaybookPath reads explicit marker", () => {
  const text =
    "Some output...\nPLAYBOOK_PATH: playbooks/blueprint-gtm-playbook-owner.html\nDone.";
  assert.equal(
    __test__.extractPlaybookPath(text),
    "playbooks/blueprint-gtm-playbook-owner.html"
  );
});

