const DEFAULT_CAT = "adj_xhr";
const DEFAULT_PLAYER_TYPE = "Batter";
const MIN_TRANSLATION_YEAR = 2016;
const MAX_TRANSLATION_YEAR = new Date().getFullYear();

const DEMO_IDENTITY = {
  contract_version: "1.0",
  player_type: DEFAULT_PLAYER_TYPE,
  player_id: "592450",
  player_name: "Judge, Aaron",
  season: 2024,
  source_team: "NYY",
  source_teams: ["NYY"],
  source_park_id: "yankee",
  source_park_ids: ["yankee"],
  source_park_name: "Yankee Stadium",
  source_park_names: ["Yankee Stadium"],
  cat: DEFAULT_CAT,
  game_types: ["R"],
  home_hr_candidate_batted_balls: 2,
  season_hr_total: 1,
  non_source_home_hr: 0,
  actual_home_hr: 1,
  source_park_hr: 1,
  source_park_matches_actual: true,
  park_average_hr: 0.13333333333333333,
  help_hurt: 0.8666666666666667,
  help_hurt_label: "Neutral",
  skipped_missing_game: 0,
  skipped_game_type: 0,
  skipped_neutral_or_alt_site: 0,
  skipped_missing_game_pks: [],
  skipped_game_type_pks: [],
  skipped_neutral_or_alt_site_pks: [],
  source_park_result: {
    rank: 3,
    park_id: "yankee",
    park_name: "Yankee Stadium",
    savant_code: "nyy",
    translated_hr: 1,
    parkshift_score: 0.8666666666666667
  },
  source_park_results: [
    {
      rank: 3,
      park_id: "yankee",
      park_name: "Yankee Stadium",
      savant_code: "nyy",
      translated_hr: 1,
      parkshift_score: 0.8666666666666667
    }
  ],
  parks: [
    {rank: 1, park_id: "minute_maid", park_name: "Minute Maid Park", savant_code: "hou", translated_hr: 2, parkshift_score: 1.8666666666666667},
    {rank: 2, park_id: "dodger", park_name: "Dodger Stadium", savant_code: "lad", translated_hr: 1, parkshift_score: 0.8666666666666667},
    {rank: 3, park_id: "yankee", park_name: "Yankee Stadium", savant_code: "nyy", translated_hr: 1, parkshift_score: 0.8666666666666667},
    {rank: 4, park_id: "american_family", park_name: "American Family Field", savant_code: "mil", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 5, park_id: "angel", park_name: "Angel Stadium", savant_code: "laa", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 6, park_id: "busch", park_name: "Busch Stadium", savant_code: "stl", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 7, park_id: "chase", park_name: "Chase Field", savant_code: "ari", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 8, park_id: "citi", park_name: "Citi Field", savant_code: "nym", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 9, park_id: "citizens_bank", park_name: "Citizens Bank Park", savant_code: "phi", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 10, park_id: "comerica", park_name: "Comerica Park", savant_code: "det", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 11, park_id: "coors", park_name: "Coors Field", savant_code: "col", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 12, park_id: "fenway", park_name: "Fenway Park", savant_code: "bos", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 13, park_id: "globe_life", park_name: "Globe Life Field", savant_code: "tex", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 14, park_id: "great_american", park_name: "Great American Ball Park", savant_code: "cin", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 15, park_id: "guaranteed_rate", park_name: "Guaranteed Rate Field", savant_code: "cws", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 16, park_id: "kauffman", park_name: "Kauffman Stadium", savant_code: "kc", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 17, park_id: "nationals", park_name: "Nationals Park", savant_code: "wsh", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 18, park_id: "oakland_coliseum", park_name: "Oakland Coliseum", savant_code: "oak", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 19, park_id: "oracle", park_name: "Oracle Park", savant_code: "sf", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 20, park_id: "camden", park_name: "Oriole Park at Camden Yards", savant_code: "bal", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 21, park_id: "pnc", park_name: "PNC Park", savant_code: "pit", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 22, park_id: "petco", park_name: "Petco Park", savant_code: "sd", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 23, park_id: "progressive", park_name: "Progressive Field", savant_code: "cle", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 24, park_id: "rogers_centre", park_name: "Rogers Centre", savant_code: "tor", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 25, park_id: "t_mobile", park_name: "T-Mobile Park", savant_code: "sea", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 26, park_id: "target", park_name: "Target Field", savant_code: "min", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 27, park_id: "tropicana", park_name: "Tropicana Field", savant_code: "tb", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 28, park_id: "truist", park_name: "Truist Park", savant_code: "atl", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 29, park_id: "wrigley", park_name: "Wrigley Field", savant_code: "chc", translated_hr: 0, parkshift_score: -0.13333333333333333},
    {rank: 30, park_id: "loan_depot", park_name: "loanDepot park", savant_code: "mia", translated_hr: 0, parkshift_score: -0.13333333333333333}
  ]
};

const EMPTY_IDENTITY = {
  contract_version: "1.0",
  player_type: DEFAULT_PLAYER_TYPE,
  player_id: "",
  player_name: "Select a player",
  season: 2024,
  source_team: "",
  source_teams: [],
  source_park_id: "",
  source_park_ids: [],
  source_park_name: "",
  source_park_names: [],
  cat: DEFAULT_CAT,
  game_types: ["R"],
  home_hr_candidate_batted_balls: 0,
  season_hr_total: 0,
  non_source_home_hr: 0,
  actual_home_hr: 0,
  source_park_hr: 0,
  source_park_matches_actual: true,
  park_average_hr: 0,
  help_hurt: 0,
  help_hurt_label: "Neutral",
  skipped_missing_game: 0,
  skipped_game_type: 0,
  skipped_neutral_or_alt_site: 0,
  parks: DEMO_IDENTITY.parks.map((park) => ({
    ...park,
    translated_hr: 0,
    projected_total_hr: 0,
    parkshift_score: 0
  }))
};

const HISTORY_KEY = "parkshift.identityHistory.v1";
const MAX_HISTORY = 30;
const HOME_PLATE = {x: 50, y: 91};
const WALL_LABEL_ANGLES = [-45, -22, 0, 22, 45];

const state = {
  data: EMPTY_IDENTITY,
  mode: "api",
  view: "full",
  sort: "rank",
  parkFilter: "",
  targetParkId: "yankee",
  selectedParkId: "",
  savedLeaderboardSort: "help_desc",
  compareKeys: new Set(),
  selectedPlayerName: "",
  selectedPlayerType: DEFAULT_PLAYER_TYPE,
  selectedCat: DEFAULT_CAT,
  queue: [],
  seasonLeaders: [],
  leaderboardOrder: "high",
  parkProfiles: {},
  showTrails: true,
  visualLoading: false,
  historyPanelOpen: false,
  leaderboardPanelOpen: true,
  savedLeaderboardOpen: false,
  history: loadHistory()
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => {
    const escapes = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"};
    return escapes[char];
  });
}

function formatNumber(value, digits = 1) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "0.0";
  }
  return number.toFixed(digits);
}

function categoryLabel(cat) {
  return cat === "adj_xhr" ? "Stadium Adjusted HR" : "Observed Flight HR";
}

function playerTypeValue(playerType) {
  return String(playerType || "").toLowerCase() === "pitcher" ? "Pitcher" : "Batter";
}

function isPitcherData(data = state.data) {
  return playerTypeValue(data?.player_type || state.selectedPlayerType) === "Pitcher";
}

function playerTypeLabel(playerType = state.selectedPlayerType) {
  return playerTypeValue(playerType) === "Pitcher" ? "Pitcher" : "Batter";
}

function hrNoun(data = state.data) {
  return isPitcherData(data) ? "HR Allowed" : "HR";
}

function sourceHomeNoun(data = state.data) {
  return isPitcherData(data) ? "home HR allowed" : "home HR";
}

function leaderNoun() {
  return state.selectedPlayerType === "Pitcher" ? "HR allowed" : "HR";
}

function leaderboardOrderLabel() {
  const pitcher = state.selectedPlayerType === "Pitcher";
  if (state.leaderboardOrder === "low") {
    return pitcher ? "fewest HR allowed" : "fewest HR";
  }
  return pitcher ? "most HR allowed" : "most HR";
}

function parkEffectName(data = state.data) {
  return isPitcherData(data) ? "Park Added" : "Park Change";
}

function selectedCat() {
  return state.selectedCat || DEFAULT_CAT;
}

function selectedPlayerType() {
  return playerTypeValue(state.selectedPlayerType);
}

function setSelectedCat(cat) {
  const nextCat = cat === "xhr" ? "xhr" : "adj_xhr";
  state.selectedCat = nextCat;
  $$("[data-cat-mode]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.catMode === nextCat);
  });
  const categoryValue = $("#categoryValue");
  if (categoryValue) {
    categoryValue.textContent = categoryLabel(nextCat);
  }
  renderQueue();
}

function setSelectedPlayerType(playerType, options = {}) {
  const nextType = playerTypeValue(playerType);
  const changed = state.selectedPlayerType !== nextType;
  state.selectedPlayerType = nextType;
  $$("[data-player-type]").forEach((button) => {
    button.classList.toggle("is-active", playerTypeValue(button.dataset.playerType) === nextType);
  });
  if (changed && options.resetSelection !== false) {
    $("#playerIdInput").value = "";
    $("#sourceTeamsInput").value = "";
    state.selectedPlayerName = "";
    state.seasonLeaders = [];
    renderSeasonLeaders();
  }
  updateCopyLabels(state.data);
  renderHistory();
  renderQueue();
}

function updateCopyLabels(data = state.data) {
  const pitcher = isPitcherData(data);
  const labels = {
    seasonHrLabel: pitcher ? "Season HR Allowed" : "Season HR",
    sourceHrLabel: pitcher ? "Home HR Allowed" : "Home HR",
    avgLabel: pitcher ? "Home Split Avg Allowed" : "Home Split Avg",
    changeLabel: pitcher ? "Park Added" : "Park Change",
    totalHrHeader: pitcher ? "Total HR Allowed" : "Total HR",
    homeHrHeader: pitcher ? "Home HR Allowed" : "Home HR",
    seasonLeadersHeading: pitcher ? "HR Allowed Leaders" : "Season Leaders",
    parkEffectLabel: pitcher ? "Park Added" : "Park Effect",
  };
  Object.entries(labels).forEach(([id, text]) => {
    const node = $(`#${id}`);
    if (node) {
      node.textContent = text;
    }
  });
  const rankOption = $("#rankSortOption");
  if (rankOption) {
    rankOption.textContent = "Best fit";
  }
  const hrHighOption = $('#sortSelect option[value="translated_hr_desc"]');
  if (hrHighOption) {
    hrHighOption.textContent = pitcher ? "HR allowed high" : "HR high";
  }
  const scoreHighOption = $('#sortSelect option[value="parkshift_score_desc"]');
  if (scoreHighOption) {
    scoreHighOption.textContent = pitcher ? "Added high" : "Score high";
  }
  const orderSelect = $("#leaderboardOrderSelect");
  if (orderSelect) {
    const highOption = orderSelect.querySelector('option[value="high"]');
    const lowOption = orderSelect.querySelector('option[value="low"]');
    if (highOption) {
      highOption.textContent = pitcher ? "Most HR Allowed" : "Most HR";
    }
    if (lowOption) {
      lowOption.textContent = pitcher ? "Fewest HR Allowed" : "Fewest HR";
    }
    orderSelect.value = state.leaderboardOrder;
  }
}

function formatInteger(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "0";
  }
  return String(Math.round(number));
}

function validSeason() {
  const input = $("#seasonInput");
  const season = Number(input.value || "2024");
  if (Number.isFinite(season) && season < MIN_TRANSLATION_YEAR) {
    input.value = String(MIN_TRANSLATION_YEAR);
    setError(`ParkShift supports seasons from ${MIN_TRANSLATION_YEAR} forward.`);
    return String(MIN_TRANSLATION_YEAR);
  }
  if (Number.isFinite(season) && season > MAX_TRANSLATION_YEAR) {
    input.value = String(MAX_TRANSLATION_YEAR);
    setError(`ParkShift supports seasons through ${MAX_TRANSLATION_YEAR}.`);
    return String(MAX_TRANSLATION_YEAR);
  }
  return input.value.trim() || "2024";
}

function seasonHrTotal(data) {
  if (data.season_hr_total !== null && data.season_hr_total !== undefined) {
    return Number(data.season_hr_total) || 0;
  }
  return Number(data.actual_home_hr) || 0;
}

function nonSourceHomeHr(data) {
  if (data.non_source_home_hr !== null && data.non_source_home_hr !== undefined) {
    return Number(data.non_source_home_hr) || 0;
  }
  return Math.max(0, seasonHrTotal(data) - (Number(data.actual_home_hr) || 0));
}

function projectedTotalHr(data, park) {
  if (!park) {
    return null;
  }
  if (park.projected_total_hr !== null && park.projected_total_hr !== undefined) {
    return Number(park.projected_total_hr) || 0;
  }
  return nonSourceHomeHr(data) + (Number(park.translated_hr) || 0);
}

function signed(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "+0.0";
  }
  return `${number >= 0 ? "+" : ""}${number.toFixed(1)}`;
}

function setStatus(message, isError = false) {
  const node = $("#runStatus");
  node.textContent = message;
  node.classList.toggle("is-error", isError);
}

function setError(message) {
  const node = $("#errorMessage");
  node.textContent = message || "";
  node.hidden = !message;
}

function displayErrorMessage(message) {
  const text = String(message || "");
  if (text.includes("No Savant Home Run Tracker detail rows found")) {
    return "No home-run detail is available for that player, season, and mode, so ParkShift cannot translate that run.";
  }
  return text;
}

function setBusy(isBusy, message) {
  $("#runButton").disabled = isBusy;
  $("#searchButton").disabled = isBusy;
  $("#addBatchButton").disabled = isBusy;
  $("#runBatchButton").disabled = isBusy;
  $("#loadLeadersButton").disabled = isBusy;
  $("#queueLeadersButton").disabled = isBusy;
  $$("[data-cat-mode]").forEach((button) => {
    button.disabled = isBusy;
  });
  $$("[data-player-type]").forEach((button) => {
    button.disabled = isBusy;
  });
  setVisualLoading(Boolean(isBusy && message && /identity|ball trail|run/i.test(message)));
  if (message) {
    setStatus(message);
  }
}

function setVisualLoading(isLoading) {
  state.visualLoading = isLoading;
  const visual = $("#parkVisual");
  if (visual) {
    visual.classList.toggle("is-loading", isLoading);
  }
}

function parkRows(data) {
  const query = state.parkFilter.trim().toLowerCase();
  const rows = [...(data.parks || [])].filter((park) => {
    if (!query) {
      return true;
    }
    return String(park.park_name || "").toLowerCase().includes(query);
  });
  return rows.sort((left, right) => {
    if (state.sort === "translated_hr_desc") {
      return Number(right.translated_hr) - Number(left.translated_hr)
        || Number(left.rank) - Number(right.rank);
    }
    if (state.sort === "parkshift_score_desc") {
      return Number(right.parkshift_score) - Number(left.parkshift_score)
        || Number(left.rank) - Number(right.rank);
    }
    if (state.sort === "worst_fit") {
      if (isPitcherData(data)) {
        return Number(right.translated_hr) - Number(left.translated_hr)
          || Number(right.parkshift_score) - Number(left.parkshift_score)
          || String(left.park_name || "").localeCompare(String(right.park_name || ""));
      }
      return Number(left.translated_hr) - Number(right.translated_hr)
        || Number(left.parkshift_score) - Number(right.parkshift_score)
        || String(left.park_name || "").localeCompare(String(right.park_name || ""));
    }
    if (state.sort === "park_name") {
      return String(left.park_name || "").localeCompare(String(right.park_name || ""));
    }
    return Number(left.rank) - Number(right.rank);
  });
}

function sourceParkIds(data) {
  if (Array.isArray(data.source_park_ids)) {
    return new Set(data.source_park_ids);
  }
  return new Set(data.source_park_id ? [data.source_park_id] : []);
}

function render(data) {
  const rows = parkRows(data);
  const best = rows[0] || {};
  const worst = rows[rows.length - 1] || {};
  const selected = selectedPark(data, best);
  const sourceTeams = Array.isArray(data.source_teams) ? data.source_teams.join(", ") : data.source_team || "";
  const pass = Boolean(data.source_park_matches_actual);
  updateCopyLabels(data);
  state.selectedPlayerType = playerTypeValue(data.player_type || state.selectedPlayerType);
  $$("[data-player-type]").forEach((button) => {
    button.classList.toggle("is-active", playerTypeValue(button.dataset.playerType) === state.selectedPlayerType);
  });

  $("#playerName").textContent = data.player_name || `Player ${data.player_id || ""}`;
  $("#playerMeta").textContent = `${sourceTeams || "Team"}, ${data.season || ""}`;
  $("#actualHr").textContent = formatInteger(seasonHrTotal(data));
  $("#sourceHr").textContent = formatInteger(data.actual_home_hr);
  $("#parkAvg").textContent = formatNumber(data.park_average_hr);
  $("#helpHurt").textContent = signed(data.help_hurt);
  $("#candidateCount").textContent = formatInteger(data.home_hr_candidate_batted_balls);
  $("#categoryValue").textContent = categoryLabel(data.cat || DEFAULT_CAT);
  $("#gameTypesValue").textContent = Array.isArray(data.game_types) ? data.game_types.join(", ") : "R";

  const validationBadge = $("#validationBadge");
  if (validationBadge) {
    validationBadge.textContent = pass ? "PASS" : "CHECK";
    validationBadge.classList.toggle("is-fail", !pass);
  }

  const isGoodEffect = isPitcherData(data) ? Number(data.help_hurt) <= 0 : Number(data.help_hurt) >= 0;
  $("#helpHurt").closest(".metric-card").classList.toggle("is-positive", isGoodEffect);
  $("#helpHurt").closest(".metric-card").classList.toggle("is-negative", !isGoodEffect);

  renderTable(data, rows);
  renderSelectedPark(data, selected, best, worst);
  renderPanelStates();
}

function renderTable(data, rows) {
  const sourceIds = sourceParkIds(data);
  const maxHr = Math.max(1, ...rows.map((park) => Number(park.translated_hr) || 0));
  $("#parksTableBody").innerHTML = rows.map((park) => {
    const hr = Number(park.translated_hr) || 0;
    const width = Math.max(4, Math.round((hr / maxHr) * 100));
    const isSource = sourceIds.has(park.park_id);
    const isSelected = park.park_id === state.selectedParkId;
    const isGoodScore = isPitcherData(data) ? Number(park.parkshift_score) <= 0 : Number(park.parkshift_score) >= 0;
    const lowClass = hr < maxHr / 2 ? " is-low" : "";
    return `
      <tr class="park-row${isSelected ? " is-selected" : ""}" data-park-id="${escapeHtml(park.park_id)}">
        <td class="rank-cell">${escapeHtml(park.rank)}</td>
        <td>
          <button class="park-name park-select-button" type="button" data-park-id="${escapeHtml(park.park_id)}">
            ${isSource ? '<span class="source-dot" aria-label="Source park"></span>' : ""}
            <span>${escapeHtml(park.park_name)}</span>
          </button>
        </td>
        <td class="hr-cell">${formatInteger(projectedTotalHr(data, park))}</td>
        <td class="hr-cell">${formatInteger(park.translated_hr)}</td>
        <td class="score-cell ${isGoodScore ? "is-good" : "is-bad"}">${signed(park.parkshift_score)}</td>
        <td class="fit-cell">
          <div class="bar-track" aria-hidden="true">
            <div class="bar-fill${lowClass}" style="width: ${width}%"></div>
          </div>
        </td>
      </tr>
    `;
  }).join("");
  $("#parksTableBody").querySelectorAll(".park-select-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedParkId = button.dataset.parkId;
      state.targetParkId = button.dataset.parkId;
      const targetSelect = $("#targetParkSelect");
      if (targetSelect) {
        targetSelect.value = state.targetParkId;
      }
      render(state.data);
      renderSavedLeaderboard();
      renderComparison();
      setStatus(`Showing ${button.textContent.trim()}`);
    });
  });
}

function allParks() {
  return [...(DEMO_IDENTITY.parks || [])].sort((left, right) => {
    return String(left.park_name || "").localeCompare(String(right.park_name || ""));
  });
}

function findPark(data, parkId) {
  return (data.parks || []).find((park) => park.park_id === parkId);
}

function parkRange(data) {
  const values = (data.parks || []).map((park) => Number(park.translated_hr) || 0);
  if (!values.length) {
    return 0;
  }
  return Math.max(...values) - Math.min(...values);
}

function selectedPark(data, fallback) {
  const selected = state.selectedParkId ? findPark(data, state.selectedParkId) : null;
  if (selected) {
    return selected;
  }
  state.selectedParkId = fallback?.park_id || "";
  return fallback || {};
}

function parkProfile(parkId) {
  return state.parkProfiles[parkId] || null;
}

function wallPoints(profile) {
  if (!profile || !Array.isArray(profile.wall)) {
    return [];
  }
  return [...profile.wall].sort((left, right) => Number(left.angle_deg) - Number(right.angle_deg));
}

function maxWallDistance(wall) {
  return Math.max(430, ...wall.map((point) => Number(point.distance_ft) || 0));
}

function svgScale(wall) {
  return 65 / maxWallDistance(wall);
}

function fieldPoint(angleDeg, distanceFt, scale) {
  const radians = Number(angleDeg) * Math.PI / 180;
  const distance = Number(distanceFt) || 0;
  return {
    x: HOME_PLATE.x + Math.sin(radians) * distance * scale,
    y: HOME_PLATE.y - Math.cos(radians) * distance * scale,
  };
}

function wallPointAtAngle(wall, angle) {
  if (!wall.length) {
    return null;
  }
  return wall.reduce((closest, point) => {
    return Math.abs(Number(point.angle_deg) - angle) < Math.abs(Number(closest.angle_deg) - angle) ? point : closest;
  }, wall[0]);
}

function ballPoint(marker, scale) {
  if (marker.spray_angle_deg === null || marker.spray_angle_deg === undefined) {
    return null;
  }
  if (marker.distance_ft === null || marker.distance_ft === undefined) {
    return null;
  }
  return fieldPoint(Number(marker.spray_angle_deg), Number(marker.distance_ft), scale);
}

function spreadOverlappingPoints(items) {
  const groups = new Map();
  items.forEach((item) => {
    if (!item.point) {
      return;
    }
    const key = `${Math.round(item.point.x / 1.5)}:${Math.round(item.point.y / 1.5)}`;
    const group = groups.get(key) || [];
    group.push(item);
    groups.set(key, group);
  });
  groups.forEach((group) => {
    if (group.length < 2) {
      return;
    }
    const radius = Math.min(3.2, 1.15 + group.length * 0.18);
    group.forEach((item, index) => {
      const angle = (Math.PI * 2 * index) / group.length;
      item.visualPoint = {
        x: item.point.x + Math.cos(angle) * radius,
        y: item.point.y + Math.sin(angle) * radius,
      };
    });
  });
  return items.map((item) => ({...item, visualPoint: item.visualPoint || item.point}));
}

function renderSelectedPark(data, park, best, worst) {
  const markers = Array.isArray(park.home_runs) ? park.home_runs : [];
  const profile = parkProfile(park.park_id);

  $("#selectedParkTitle").textContent = park.park_name || "No park";
  $("#selectedParkMeta").textContent = `${formatInteger(projectedTotalHr(data, park))} total ${hrNoun(data).toLowerCase()}, ${formatInteger(park.translated_hr)} ${sourceHomeNoun(data)}`;
  const selectedChange = $("#selectedParkChange");
  const isGoodScore = isPitcherData(data) ? Number(park.parkshift_score) <= 0 : Number(park.parkshift_score) >= 0;
  selectedChange.textContent = signed(park.parkshift_score);
  selectedChange.classList.toggle("is-good", isGoodScore);
  selectedChange.classList.toggle("is-bad", !isGoodScore);
  $("#parkVisual").innerHTML = renderParkVisualSvg(park, markers, profile);
  bindBallTooltips();
}

function renderParkVisualSvg(park, markers, profile) {
  const wall = wallPoints(profile);
  if (!wall.length) {
    return `
      <svg class="park-map" viewBox="0 0 100 100" role="img" aria-label="${escapeHtml(park.park_name || "Selected park")} home run map">
        <rect class="park-sky" x="0" y="0" width="100" height="100"></rect>
        <text class="park-empty-text" x="50" y="48" text-anchor="middle">Loading park dimensions</text>
      </svg>
    `;
  }
  const scale = svgScale(wall);
  const wallSvgPoints = wall.map((point) => fieldPoint(point.angle_deg, point.distance_ft, scale));
  const wallPath = wallSvgPoints.map((point, index) => {
    return `${index === 0 ? "M" : "L"}${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
  }).join(" ");
  const outfieldPoints = [
    `${HOME_PLATE.x},${HOME_PLATE.y}`,
    ...wallSvgPoints.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`),
    `${HOME_PLATE.x},${HOME_PLATE.y}`,
  ].join(" ");
  const plottedMarkers = spreadOverlappingPoints(
    markers.slice(0, 80).map((marker, index) => ({
      marker,
      index,
      point: ballPoint(marker, scale),
    }))
  );
  const trailMarkup = plottedMarkers.map((item) => {
    if (!item.point || !item.visualPoint) {
      return "";
    }
    const {marker, visualPoint} = item;
    const controlX = 50 + (visualPoint.x - 50) * 0.44;
    const controlY = Math.max(9, Math.min(visualPoint.y, 88) - 18);
    const titleText = ballTooltipText(marker);
    const tooltip = escapeHtml(titleText);
    const trail = state.showTrails
      ? `<path class="flight-trail" data-ball-tooltip="${tooltip}" d="M${HOME_PLATE.x} ${HOME_PLATE.y} Q${controlX.toFixed(1)} ${controlY.toFixed(1)} ${visualPoint.x.toFixed(1)} ${visualPoint.y.toFixed(1)}"></path>`
      : "";
    return `
      ${trail}
      <circle class="flight-dot" data-ball-tooltip="${tooltip}" cx="${visualPoint.x.toFixed(1)}" cy="${visualPoint.y.toFixed(1)}" r="1.7"></circle>
      <circle class="flight-hotspot" data-ball-tooltip="${tooltip}" cx="${visualPoint.x.toFixed(1)}" cy="${visualPoint.y.toFixed(1)}" r="4"></circle>
    `;
  }).join("");
  const dimensionLabels = WALL_LABEL_ANGLES.map((angle) => {
    const wallPoint = wallPointAtAngle(wall, angle);
    const svgPoint = fieldPoint(wallPoint.angle_deg, wallPoint.distance_ft - 18, scale);
    return `<text class="dimension-label" x="${svgPoint.x.toFixed(1)}" y="${svgPoint.y.toFixed(1)}" text-anchor="middle">${formatInteger(wallPoint.distance_ft)}</text>`;
  }).join("");
  const empty = trailMarkup.trim()
    ? ""
    : '<text class="park-empty-text" x="50" y="33" text-anchor="middle">Loading ball trails</text>';
  return `
    <svg class="park-map" viewBox="0 0 100 100" role="img" aria-label="${escapeHtml(park.park_name || "Selected park")} home run map">
      <rect class="park-sky" x="0" y="0" width="100" height="100"></rect>
      <polygon class="park-outfield" points="${outfieldPoints}"></polygon>
      <path class="park-wall" d="${wallPath}"></path>
      <polygon class="infield-dirt" points="50,63 65,78 50,93 35,78"></polygon>
      <polygon class="infield-grass" points="50,73 57,80 50,87 43,80"></polygon>
      <circle class="mound" cx="50" cy="80" r="1.4"></circle>
      <text class="park-map-label" x="50" y="12" text-anchor="middle">${escapeHtml(park.park_name || "Selected Park")}</text>
      ${dimensionLabels}
      ${trailMarkup}
      ${empty}
    </svg>
  `;
}

function ballTooltipText(marker) {
  const parts = [
    marker.game_date || `Game ${marker.game_pk}`,
    marker.distance_ft ? `${marker.distance_ft} ft` : null,
    marker.exit_velocity ? `${formatNumber(marker.exit_velocity, 1)} mph EV` : null,
    marker.launch_angle ? `${marker.launch_angle} deg LA` : null,
    marker.spray_angle_deg !== null && marker.spray_angle_deg !== undefined ? `${formatNumber(marker.spray_angle_deg, 1)} deg spray` : null,
  ].filter(Boolean);
  return parts.join("\n");
}

function bindBallTooltips() {
  const tooltip = $("#ballTooltip");
  if (!tooltip) {
    return;
  }
  $$("#parkVisual [data-ball-tooltip]").forEach((node) => {
    node.addEventListener("mouseenter", (event) => {
      tooltip.innerHTML = tooltipHtml(event.currentTarget.dataset.ballTooltip || "");
      tooltip.hidden = false;
      positionTooltip(event);
    });
    node.addEventListener("mousemove", positionTooltip);
    node.addEventListener("mouseleave", () => {
      tooltip.hidden = true;
    });
  });
}

function tooltipHtml(text) {
  const lines = String(text || "").split("\n").filter(Boolean);
  if (!lines.length) {
    return "";
  }
  const [title, ...rest] = lines;
  return `
    <div class="tooltip-title">${escapeHtml(title)}</div>
    ${rest.length ? `<div class="tooltip-meta">${rest.map(escapeHtml).join("<br>")}</div>` : ""}
  `;
}

function positionTooltip(event) {
  const tooltip = $("#ballTooltip");
  if (!tooltip || tooltip.hidden) {
    return;
  }
  const offset = 14;
  const width = tooltip.offsetWidth || 190;
  const height = tooltip.offsetHeight || 80;
  const left = Math.min(window.innerWidth - width - 8, event.clientX + offset);
  const top = Math.min(window.innerHeight - height - 8, event.clientY + offset);
  tooltip.style.left = `${Math.max(8, left)}px`;
  tooltip.style.top = `${Math.max(8, top)}px`;
}

function renderPanelStates() {
  const historyPanel = $("#runHistory")?.closest(".workflow-panel");
  const leadersPanel = $("#seasonLeaders")?.closest(".workflow-panel");
  const savedPanel = $("#savedLeaderboard")?.closest(".analysis-panel");
  if (historyPanel) {
    historyPanel.classList.toggle("is-collapsed", !state.historyPanelOpen);
  }
  if (leadersPanel) {
    leadersPanel.classList.toggle("is-collapsed", !state.leaderboardPanelOpen);
  }
  if (savedPanel) {
    savedPanel.classList.toggle("is-collapsed", !state.savedLeaderboardOpen);
  }
  const historyButton = $("#toggleHistoryPanelButton");
  if (historyButton) {
    historyButton.textContent = state.historyPanelOpen ? "Hide" : "Show";
  }
  const leadersButton = $("#toggleLeadersPanelButton");
  if (leadersButton) {
    leadersButton.textContent = state.leaderboardPanelOpen ? "Hide" : "Show";
  }
  const savedButton = $("#toggleSavedLeaderboardButton");
  if (savedButton) {
    savedButton.textContent = state.savedLeaderboardOpen ? "Hide" : "Show";
  }
  const trailsButton = $("#toggleTrailsButton");
  if (trailsButton) {
    trailsButton.textContent = state.showTrails ? "Hide Trails" : "Show Trails";
  }
}

function populateTargetParkSelect() {
  const select = $("#targetParkSelect");
  if (!select) {
    return;
  }
  select.innerHTML = allParks().map((park) => {
    const selected = park.park_id === state.targetParkId ? " selected" : "";
    return `<option value="${escapeHtml(park.park_id)}"${selected}>${escapeHtml(park.park_name)}</option>`;
  }).join("");
}

function renderTargetPark() {
  const readout = $("#targetParkReadout");
  if (!readout) {
    return;
  }
  const current = findPark(state.data, state.targetParkId);
  if (!current) {
    readout.innerHTML = '<div class="mini-title">No target data</div>';
    return;
  }
  const savedFits = state.history
    .map((entry) => ({entry, park: findPark(entry.data, state.targetParkId)}))
    .filter((item) => item.park)
    .sort((left, right) => Number(right.park.translated_hr) - Number(left.park.translated_hr));
  const leader = savedFits[0];
  readout.innerHTML = `
    <div class="target-main">
      <strong>${formatInteger(current.translated_hr)} HR</strong>
      <span>${formatInteger(projectedTotalHr(state.data, current))} total ${escapeHtml(hrNoun(state.data).toLowerCase())}, ${signed(current.parkshift_score)} home split change for ${escapeHtml(current.park_name)}</span>
    </div>
    <div class="mini-meta">${leader ? `Top saved fit: ${escapeHtml(leader.entry.data.player_name || leader.entry.data.player_id)} (${formatInteger(projectedTotalHr(leader.entry.data, leader.park))} total HR)` : "Saved run target rankings appear after batch runs."}</div>
  `;
}

function setMode(nextMode) {
  state.mode = nextMode;
  $$("[data-mode]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.mode === nextMode);
  });
  setStatus(nextMode === "demo" ? "Demo data loaded" : "API mode ready");
  if (nextMode === "demo") {
    state.data = DEMO_IDENTITY;
    render(state.data);
  }
}

function setView(nextView) {
  state.view = nextView;
  document.body.classList.remove("view-full", "view-help-hurt", "view-parkshift-score");
  document.body.classList.add(`view-${nextView}`);
  $$("[data-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === nextView);
  });
}

function sourceTeamValues() {
  return $("#sourceTeamsInput").value
    .split(/[,\s]+/)
    .map((value) => value.trim().toUpperCase())
    .filter(Boolean);
}

function currentRunSpec() {
  const playerId = $("#playerIdInput").value.trim();
  const season = validSeason();
  const sourceTeams = sourceTeamValues();
  const cat = selectedCat();
  return {
    playerId,
    season,
    sourceTeams,
    cat,
    playerType: selectedPlayerType(),
    label: state.selectedPlayerName || `Player ${playerId}`
  };
}

async function fetchIdentity(spec, options = {}) {
  const params = new URLSearchParams();

  if (spec.playerId) {
    params.set("player_id", spec.playerId);
  }
  if (spec.season) {
    params.set("year", spec.season);
  }
  params.set("cat", spec.cat || DEFAULT_CAT);
  params.set("player_type", spec.playerType || selectedPlayerType());
  if (options.noCache === true) {
    params.set("no_cache", "true");
  }
  spec.sourceTeams.forEach((team) => params.append("source_teams", team));

  const response = await fetch(`${apiBase()}/identity?${params.toString()}`);
  const payload = await response.json().catch(() => ({}));
  console.debug("ParkShift identity response", {
    playerId: spec.playerId,
    season: spec.season,
    cache: response.headers.get("x-parkshift-cache") || "unknown",
    status: response.status,
  });
  if (!response.ok) {
    throw new Error(payload.detail || payload.error || `API returned ${response.status}`);
  }
  return payload;
}

function identityRunSpec(data) {
  return {
    playerId: String(data.player_id || ""),
    season: String(data.season || validSeason()),
    sourceTeams: [],
    cat: data.cat || DEFAULT_CAT,
    playerType: playerTypeValue(data.player_type || state.selectedPlayerType),
    label: data.player_name || `Player ${data.player_id || ""}`
  };
}

function hasCoordinateBackedTrails(data) {
  return (data.parks || []).some((park) => {
    return (park.home_runs || []).some((marker) => {
      return marker.spray_angle_deg !== null && marker.spray_angle_deg !== undefined;
    });
  });
}

async function hydrateCurrentRunTrails(reason = "Loading ball trails") {
  if (!state.data?.player_id || hasCoordinateBackedTrails(state.data)) {
    return;
  }
  try {
    setStatus(reason);
    const payload = await fetchIdentity(identityRunSpec(state.data));
    state.data = payload;
    saveHistory(payload);
    render(payload);
    setStatus("Ball trails loaded");
  } catch (error) {
    setStatus(displayErrorMessage(error.message || "Ball trails unavailable"), true);
  }
}

async function runApi() {
  setBusy(true, "Loading identity data");
  setError("");
  const payload = await fetchIdentity(currentRunSpec());
  state.data = payload;
  state.selectedParkId = "";
  render(payload);
  saveHistory(payload);
  setStatus("API result loaded");
}

async function handleRun() {
  if (!$("#playerIdInput").value.trim()) {
    setError("Search and select a player before running.");
    return;
  }

  try {
    await runApi();
  } catch (error) {
    const message = displayErrorMessage(error.message || "API request failed");
    setStatus("Run failed", true);
    setError(message);
  } finally {
    setBusy(false);
  }
}

function apiBase() {
  return $("#apiBaseInput").value.replace(/\/+$/, "");
}

async function handleSearch() {
  const query = $("#playerSearchInput").value.trim();
  const season = validSeason();
  if (!query) {
    setError("Enter a player name to search.");
    return;
  }
  try {
    setBusy(true, "Searching players");
    setError("");
    const params = new URLSearchParams({query, year: season || "2024", limit: "8", cat: selectedCat(), player_type: selectedPlayerType()});
    const response = await fetch(`${apiBase()}/players?${params.toString()}`);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || payload.error || `API returned ${response.status}`);
    }
    renderPlayerResults(payload.players || []);
    setStatus(`${(payload.players || []).length} player result${(payload.players || []).length === 1 ? "" : "s"}`);
  } catch (error) {
    const message = displayErrorMessage(error.message || "Player search failed");
    setStatus("Search failed", true);
    setError(message);
  } finally {
    setBusy(false);
  }
}

function renderPlayerResults(players) {
  const container = $("#playerResults");
  if (!players.length) {
    container.innerHTML = '<span class="player-result">No players found</span>';
    return;
  }
  container.innerHTML = players.map((player) => `
    <button class="player-result" type="button" data-player-id="${escapeHtml(player.player_id)}" data-team="${escapeHtml(player.team_abbrev)}" data-player-name="${escapeHtml(player.player)}">
      ${escapeHtml(player.player)}
      <span>${escapeHtml(player.team_abbrev)} · ${formatInteger(player.hr_total)} ${escapeHtml(leaderNoun())}</span>
    </button>
  `).join("");
  container.querySelectorAll(".player-result[data-player-id]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#playerIdInput").value = button.dataset.playerId;
      $("#sourceTeamsInput").value = "";
      state.selectedPlayerName = button.dataset.playerName || `Player ${button.dataset.playerId}`;
      setStatus(`Selected ${button.textContent.trim()}`);
    });
  });
}

function runKey(spec) {
  return `${spec.playerId}:${spec.season}:${spec.sourceTeams.join("+")}:${spec.cat || DEFAULT_CAT}:${spec.playerType || DEFAULT_PLAYER_TYPE}`;
}

function playerToRunSpec(player) {
  return {
    playerId: String(player.player_id || ""),
    season: validSeason(),
    sourceTeams: [],
    cat: selectedCat(),
    playerType: selectedPlayerType(),
    label: player.player || `Player ${player.player_id}`,
    status: "pending"
  };
}

function addSpecToQueue(spec) {
  if (!spec.playerId) {
    return false;
  }
  if (!state.queue.some((item) => runKey(item) === runKey(spec))) {
    state.queue.push({...spec, status: spec.status || "pending"});
    return true;
  }
  return false;
}

function historyKey(data) {
  const teams = Array.isArray(data.source_teams) ? data.source_teams.join("+") : data.source_team || "";
  return `${data.player_id}:${data.season}:${teams}:${data.cat || DEFAULT_CAT}:${playerTypeValue(data.player_type)}`;
}

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function compactIdentityForStorage(data) {
  return data;
}

function persistHistory() {
  const fullHistory = state.history.slice(0, MAX_HISTORY).map((entry) => ({
    ...entry,
    data: compactIdentityForStorage(entry.data)
  }));
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(fullHistory));
  } catch {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(fullHistory.slice(0, 5)));
  }
}

function saveHistory(data) {
  const entry = {
    key: historyKey(data),
    savedAt: new Date().toISOString(),
    data
  };
  state.history = [entry, ...state.history.filter((item) => item.key !== entry.key)].slice(0, MAX_HISTORY);
  persistHistory();
  renderHistory();
  renderSavedLeaderboard();
  renderComparison();
  renderTargetPark();
}

function renderHistory() {
  const container = $("#runHistory");
  const entries = state.history
    .map((entry, index) => ({entry, index}))
    .filter(({entry}) => playerTypeValue(entry.data?.player_type) === selectedPlayerType());
  if (!entries.length) {
    container.innerHTML = `<div class="mini-item"><div><div class="mini-title">No ${escapeHtml(playerTypeLabel())} runs saved</div><div class="mini-meta">Completed ${escapeHtml(playerTypeLabel().toLowerCase())} reports appear here</div></div></div>`;
    return;
  }
  container.innerHTML = entries.map(({entry, index}) => {
    const data = entry.data;
    const teams = Array.isArray(data.source_teams) ? data.source_teams.join(", ") : data.source_team || "";
    return `
      <div class="mini-item">
        <div>
          <div class="mini-title">${escapeHtml(data.player_name || data.player_id)}</div>
          <div class="mini-meta">${escapeHtml(data.season)} · ${escapeHtml(playerTypeLabel(data.player_type))} · ${escapeHtml(categoryLabel(data.cat || DEFAULT_CAT))} · ${escapeHtml(teams)} · ${formatInteger(seasonHrTotal(data))} ${escapeHtml(hrNoun(data))} · Change ${signed(data.help_hurt)}</div>
        </div>
        <div class="mini-actions">
          <button type="button" data-history-index="${index}">Open</button>
        </div>
      </div>
    `;
  }).join("");
  container.querySelectorAll("[data-history-index]").forEach((button) => {
    button.addEventListener("click", async () => {
      const entry = state.history[Number(button.dataset.historyIndex)];
      if (!entry) {
        return;
      }
      state.data = entry.data;
      state.selectedPlayerName = entry.data.player_name || "";
      state.selectedParkId = "";
      state.selectedPlayerType = playerTypeValue(entry.data.player_type);
      setSelectedPlayerType(state.selectedPlayerType, {resetSelection: false});
      setSelectedCat(entry.data.cat || DEFAULT_CAT);
      $("#playerIdInput").value = entry.data.player_id || "";
      $("#seasonInput").value = entry.data.season || "";
      $("#sourceTeamsInput").value = "";
      render(entry.data);
      setStatus("Saved run loaded");
      await hydrateCurrentRunTrails("Loading saved run ball trails");
    });
  });
}

function selectedComparisonEntries() {
  const selected = state.history.filter((entry) => state.compareKeys.has(entry.key));
  return selected.length ? selected : state.history.slice(0, 4);
}

function renderComparison() {
  const table = $("#comparisonTable");
  if (!table) {
    return;
  }
  const entries = selectedComparisonEntries();
  if (!entries.length) {
    table.innerHTML = '<div class="mini-item"><div><div class="mini-title">No runs to compare</div><div class="mini-meta">Run players, then select Compare</div></div></div>';
    return;
  }
  const rows = entries.map((entry) => {
    const data = entry.data;
    const best = [...(data.parks || [])].sort((left, right) => Number(left.rank) - Number(right.rank))[0] || {};
    const target = findPark(data, state.targetParkId);
    return `
      <tr>
        <td>${escapeHtml(data.player_name || data.player_id)}</td>
        <td>${escapeHtml(categoryLabel(data.cat || DEFAULT_CAT))}</td>
        <td>${escapeHtml(Array.isArray(data.source_teams) ? data.source_teams.join(", ") : data.source_team || "")}</td>
        <td>${formatInteger(seasonHrTotal(data))}</td>
        <td>${formatNumber(data.park_average_hr)}</td>
        <td>${signed(data.help_hurt)}</td>
        <td>${escapeHtml(best.park_name || "")}</td>
        <td>${target ? formatInteger(projectedTotalHr(data, target)) : "-"}</td>
      </tr>
    `;
  }).join("");
  table.innerHTML = `
    <table class="compare-table">
      <thead>
        <tr>
          <th>Player</th>
          <th>Mode</th>
          <th>Teams</th>
          <th>Season</th>
          <th>Avg</th>
          <th>Help</th>
          <th>Best</th>
          <th>Target</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderSavedLeaderboard() {
  const container = $("#savedLeaderboard");
  if (!container) {
    return;
  }
  const entries = [...state.history];
  if (!entries.length) {
    container.innerHTML = '<div class="mini-item"><div><div class="mini-title">No saved runs</div><div class="mini-meta">Batch results appear here</div></div></div>';
    return;
  }
  entries.sort((left, right) => {
    if (state.savedLeaderboardSort === "help_asc") {
      return Number(left.data.help_hurt) - Number(right.data.help_hurt);
    }
    if (state.savedLeaderboardSort === "sensitivity_desc") {
      return parkRange(right.data) - parkRange(left.data);
    }
    if (state.savedLeaderboardSort === "target_desc") {
      return Number(findPark(right.data, state.targetParkId)?.translated_hr || 0) - Number(findPark(left.data, state.targetParkId)?.translated_hr || 0);
    }
    return Number(right.data.help_hurt) - Number(left.data.help_hurt);
  });
  container.innerHTML = entries.slice(0, 8).map((entry, index) => {
    const data = entry.data;
    const target = findPark(data, state.targetParkId);
    const metric = state.savedLeaderboardSort === "target_desc"
      ? `${formatInteger(projectedTotalHr(data, target))} target HR`
      : state.savedLeaderboardSort === "sensitivity_desc"
        ? `${formatInteger(parkRange(data))} HR range`
        : `${signed(data.help_hurt)} ${escapeHtml(parkEffectName(data))}`;
    return `
      <div class="mini-item">
        <div>
          <div class="mini-title">${index + 1}. ${escapeHtml(data.player_name || data.player_id)}</div>
          <div class="mini-meta">${escapeHtml(categoryLabel(data.cat || DEFAULT_CAT))} · ${escapeHtml(metric)}</div>
        </div>
        <button type="button" data-leader-key="${escapeHtml(entry.key)}">Open</button>
      </div>
    `;
  }).join("");
  container.querySelectorAll("[data-leader-key]").forEach((button) => {
    button.addEventListener("click", async () => {
      const entry = state.history.find((item) => item.key === button.dataset.leaderKey);
      if (!entry) {
        return;
      }
      state.data = entry.data;
      state.selectedParkId = "";
      setSelectedCat(entry.data.cat || DEFAULT_CAT);
      render(entry.data);
      setStatus("Leaderboard run loaded");
      await hydrateCurrentRunTrails("Loading leaderboard ball trails");
    });
  });
}

function renderQueue() {
  const container = $("#batchQueue");
  if (!state.queue.length) {
    container.innerHTML = '<div class="mini-item"><div><div class="mini-title">Queue is empty</div><div class="mini-meta">Select players and click Queue</div></div></div>';
    return;
  }
  container.innerHTML = state.queue.map((item, index) => `
    <div class="mini-item">
      <div>
        <div class="mini-title">${escapeHtml(item.label)}</div>
      <div class="mini-meta">${escapeHtml(item.season)} · ${escapeHtml(item.playerType || DEFAULT_PLAYER_TYPE)} · ${escapeHtml(categoryLabel(item.cat || DEFAULT_CAT))} · auto source · ${escapeHtml(item.status || "pending")}</div>
      </div>
      <button type="button" data-remove-queue="${index}">Remove</button>
    </div>
  `).join("");
  container.querySelectorAll("[data-remove-queue]").forEach((button) => {
    button.addEventListener("click", () => {
      state.queue.splice(Number(button.dataset.removeQueue), 1);
      renderQueue();
    });
  });
}

function handleAddBatch() {
  const spec = currentRunSpec();
  if (!spec.playerId) {
    setError("Select or enter a player before adding to the queue.");
    return;
  }
  addSpecToQueue({...spec, status: "pending"});
  renderQueue();
  setError("");
  setStatus("Added to batch queue");
}

async function handleLoadLeaders() {
  try {
    setBusy(true, "Loading season leaders");
    setError("");
    const params = new URLSearchParams({
      year: validSeason(),
      limit: $("#leaderLimitSelect").value || "10",
      cat: selectedCat(),
      player_type: selectedPlayerType(),
      order: state.leaderboardOrder,
    });
    const response = await fetch(`${apiBase()}/leaderboard?${params.toString()}`);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || payload.error || `API returned ${response.status}`);
    }
    state.seasonLeaders = payload.players || [];
    renderSeasonLeaders();
    setStatus(`${state.seasonLeaders.length} qualified ${leaderboardOrderLabel()} leaders loaded`);
  } catch (error) {
    const message = displayErrorMessage(error.message || "Season leaders failed");
    setStatus("Season leaders failed", true);
    setError(message);
  } finally {
    setBusy(false);
  }
}

async function loadParkProfiles() {
  try {
    const response = await fetch(`${apiBase()}/parks`);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || payload.error || `API returned ${response.status}`);
    }
    state.parkProfiles = payload.parks || {};
    render(state.data);
  } catch {
    state.parkProfiles = {};
  }
}

function renderSeasonLeaders() {
  const container = $("#seasonLeaders");
  if (!state.seasonLeaders.length) {
    container.innerHTML = '<div class="mini-item"><div><div class="mini-title">No qualified leaders loaded</div><div class="mini-meta">Load qualified players for this season</div></div></div>';
    return;
  }
  container.innerHTML = state.seasonLeaders.map((player, index) => `
    <div class="mini-item">
      <div>
        <div class="mini-title">${index + 1}. ${escapeHtml(player.player)}</div>
        <div class="mini-meta">${escapeHtml(player.team_abbrev)} · ${formatInteger(player.hr_total)} ${escapeHtml(leaderNoun())}</div>
      </div>
      <div class="mini-actions">
        <button type="button" data-leader-select="${index}">Select</button>
        <button type="button" data-leader-queue="${index}">Queue</button>
      </div>
    </div>
  `).join("");
  container.querySelectorAll("[data-leader-select]").forEach((button) => {
    button.addEventListener("click", () => {
      const player = state.seasonLeaders[Number(button.dataset.leaderSelect)];
      if (!player) {
        return;
      }
      $("#playerIdInput").value = player.player_id || "";
      $("#sourceTeamsInput").value = "";
      $("#playerSearchInput").value = player.player || "";
      state.selectedPlayerName = player.player || "";
      setStatus(`Selected ${player.player}`);
    });
  });
  container.querySelectorAll("[data-leader-queue]").forEach((button) => {
    button.addEventListener("click", () => {
      const player = state.seasonLeaders[Number(button.dataset.leaderQueue)];
      if (!player) {
        return;
      }
      const added = addSpecToQueue(playerToRunSpec(player));
      renderQueue();
      setStatus(added ? `Queued ${player.player}` : `${player.player} already queued`);
    });
  });
}

function handleQueueLeaders() {
  if (!state.seasonLeaders.length) {
    setError("Load season leaders before queueing them.");
    return;
  }
  let added = 0;
  state.seasonLeaders.forEach((player) => {
    if (addSpecToQueue(playerToRunSpec(player))) {
      added += 1;
    }
  });
  renderQueue();
  setError("");
  setStatus(`${added} leader${added === 1 ? "" : "s"} queued`);
}

async function handleRunBatch() {
  if (state.mode === "demo") {
    setError("Batch runs use API mode.");
    return;
  }
  if (!state.queue.length) {
    handleAddBatch();
  }
  if (!state.queue.length) {
    return;
  }

  const failures = [];
  setBusy(true, `Running 1 of ${state.queue.length}`);
  setError("");
  for (let index = 0; index < state.queue.length; index += 1) {
    const spec = state.queue[index];
    try {
      spec.status = "running";
      renderQueue();
      setStatus(`Running ${index + 1} of ${state.queue.length}: ${spec.label}`);
      const payload = await fetchIdentity(spec);
      state.data = payload;
      state.selectedParkId = "";
      render(payload);
      saveHistory(payload);
      spec.status = "done";
      renderQueue();
    } catch (error) {
      spec.status = "failed";
      renderQueue();
      failures.push(`${spec.label}: ${displayErrorMessage(error.message || "failed")}`);
    }
  }
  setBusy(false);
  if (failures.length) {
    setError(failures.join(" | "));
    setStatus(`${state.queue.length - failures.length} completed, ${failures.length} failed`, true);
  } else {
    setStatus(`${state.queue.length} batch run${state.queue.length === 1 ? "" : "s"} completed`);
    state.queue = [];
    renderQueue();
  }
}

function toggleSourceTeam(team) {
  const teams = new Set(sourceTeamValues());
  if (teams.has(team)) {
    teams.delete(team);
  } else {
    teams.add(team);
  }
  $("#sourceTeamsInput").value = Array.from(teams).join(" ");
}

function currentRowsForExport() {
  return parkRows(state.data);
}

function handleExportCsv() {
  const header = ["rank", "park_name", "translated_hr", "parkshift_score"];
  const lines = [header.join(",")];
  currentRowsForExport().forEach((park) => {
    lines.push([
      park.rank,
      `"${String(park.park_name || "").replaceAll('"', '""')}"`,
      park.translated_hr,
      Number(park.parkshift_score || 0).toFixed(3)
    ].join(","));
  });
  const blob = new Blob([`${lines.join("\n")}\n`], {type: "text/csv"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `parkshift-${state.data.player_id || "player"}-${state.data.season || "season"}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  setStatus("CSV exported");
}

function csvEscape(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function exportRows(filename, header, rows) {
  const lines = [header.join(",")];
  rows.forEach((row) => {
    lines.push(row.map(csvEscape).join(","));
  });
  const blob = new Blob([`${lines.join("\n")}\n`], {type: "text/csv"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function handleExportHistory() {
  const rows = state.history.map((entry) => {
    const data = entry.data;
    const target = findPark(data, state.targetParkId);
    return [
      data.player_id,
      data.player_name,
      data.season,
      Array.isArray(data.source_teams) ? data.source_teams.join(" ") : data.source_team || "",
      seasonHrTotal(data),
      data.actual_home_hr,
      data.source_park_hr,
      Number(data.park_average_hr || 0).toFixed(3),
      Number(data.help_hurt || 0).toFixed(3),
      target?.park_name || "",
      target ? projectedTotalHr(data, target) : "",
    ];
  });
  exportRows("parkshift-saved-runs.csv", ["player_id", "player", "season", "source_teams", "season_hr_total", "actual_home_hr", "source_park_hr", "park_average_hr", "help_hurt", "target_park", "target_total_hr"], rows);
  setStatus("Saved runs exported");
}

function handleExportComparison() {
  const rows = selectedComparisonEntries().map((entry) => {
    const data = entry.data;
    const target = findPark(data, state.targetParkId);
    return [
      data.player_id,
      data.player_name,
      Array.isArray(data.source_teams) ? data.source_teams.join(" ") : data.source_team || "",
      seasonHrTotal(data),
      Number(data.park_average_hr || 0).toFixed(3),
      Number(data.help_hurt || 0).toFixed(3),
      target ? projectedTotalHr(data, target) : "",
    ];
  });
  exportRows("parkshift-comparison.csv", ["player_id", "player", "source_teams", "season_hr_total", "park_average_hr", "help_hurt", "target_total_hr"], rows);
  setStatus("Comparison exported");
}

async function handleShare() {
  const url = new URL(window.location.href);
  url.searchParams.set("player_id", $("#playerIdInput").value.trim());
  url.searchParams.set("year", validSeason());
  url.searchParams.set("source_teams", $("#sourceTeamsInput").value.trim());
  url.searchParams.set("cat", selectedCat());
  url.searchParams.set("player_type", selectedPlayerType());
  try {
    await navigator.clipboard.writeText(url.toString());
    setStatus("Share link copied");
  } catch {
    setStatus(url.toString());
  }
}

function bindEvents() {
  $$("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => setMode(button.dataset.mode));
  });
  $$("[data-view]").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.view));
  });
  $$("[data-player-type]").forEach((button) => {
    button.addEventListener("click", () => {
      const previousType = state.selectedPlayerType;
      setSelectedPlayerType(button.dataset.playerType);
      if (previousType !== state.selectedPlayerType) {
        state.data = {...EMPTY_IDENTITY, player_type: state.selectedPlayerType, season: Number(validSeason()) || 2024};
        state.selectedParkId = "";
        render(state.data);
        setStatus(`${playerTypeLabel()} mode selected`);
      }
    });
  });
  $("#runButton").addEventListener("click", handleRun);
  $("#searchButton").addEventListener("click", handleSearch);
  $("#addBatchButton").addEventListener("click", handleAddBatch);
  $("#runBatchButton").addEventListener("click", handleRunBatch);
  $("#loadLeadersButton").addEventListener("click", handleLoadLeaders);
  $("#queueLeadersButton").addEventListener("click", handleQueueLeaders);
  $("#leaderLimitSelect").addEventListener("change", () => {
    if (state.seasonLeaders.length) {
      handleLoadLeaders();
    }
  });
  $("#leaderboardOrderSelect").addEventListener("change", (event) => {
    state.leaderboardOrder = event.target.value === "low" ? "low" : "high";
    if (state.seasonLeaders.length) {
      handleLoadLeaders();
    } else {
      setStatus(`${leaderboardOrderLabel()} leaderboard selected`);
    }
  });
  $("#toggleLeadersPanelButton").addEventListener("click", () => {
    state.leaderboardPanelOpen = !state.leaderboardPanelOpen;
    renderPanelStates();
  });
  $$("[data-cat-mode]").forEach((button) => {
    button.addEventListener("click", async () => {
      const previousCat = state.selectedCat;
      setSelectedCat(button.dataset.catMode);
      state.seasonLeaders = [];
      renderSeasonLeaders();
      if (state.data?.player_id && previousCat !== state.selectedCat) {
        try {
          setBusy(true, `Loading ${categoryLabel(state.selectedCat)}`);
          const payload = await fetchIdentity(identityRunSpec({...state.data, cat: state.selectedCat}));
          state.data = payload;
          state.selectedParkId = "";
          render(payload);
          saveHistory(payload);
          setStatus(`${categoryLabel(state.selectedCat)} loaded`);
        } catch (error) {
          setStatus(displayErrorMessage(error.message || "Mode switch failed"), true);
        } finally {
          setBusy(false);
        }
      } else {
        setStatus(`${categoryLabel(state.selectedCat)} mode selected`);
      }
    });
  });
  $("#clearBatchButton").addEventListener("click", () => {
    state.queue = [];
    renderQueue();
  });
  $("#toggleHistoryPanelButton").addEventListener("click", () => {
    state.historyPanelOpen = !state.historyPanelOpen;
    renderPanelStates();
  });
  $("#toggleSavedLeaderboardButton")?.addEventListener("click", () => {
    state.savedLeaderboardOpen = !state.savedLeaderboardOpen;
    renderPanelStates();
  });
  $("#toggleTrailsButton").addEventListener("click", () => {
    state.showTrails = !state.showTrails;
    render(state.data);
  });
  $("#clearHistoryButton").addEventListener("click", () => {
    state.history = [];
    state.compareKeys = new Set();
    persistHistory();
    renderHistory();
    renderSavedLeaderboard();
    renderComparison();
    renderTargetPark();
  });
  $("#exportHistoryButton").addEventListener("click", handleExportHistory);
  $("#exportComparisonButton")?.addEventListener("click", handleExportComparison);
  $$("[data-source-team]").forEach((button) => {
    button.addEventListener("click", () => toggleSourceTeam(button.dataset.sourceTeam));
  });
  $("#playerSearchInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSearch();
    }
  });
  $("#parkFilterInput").addEventListener("input", (event) => {
    state.parkFilter = event.target.value;
    renderTable(state.data, parkRows(state.data));
  });
  $("#sortSelect").addEventListener("change", (event) => {
    state.sort = event.target.value;
    renderTable(state.data, parkRows(state.data));
  });
  $("#targetParkSelect")?.addEventListener("change", (event) => {
    state.targetParkId = event.target.value;
    state.selectedParkId = event.target.value;
    render(state.data);
    renderSavedLeaderboard();
    renderComparison();
  });
  $("#savedLeaderboardSort")?.addEventListener("change", (event) => {
    state.savedLeaderboardSort = event.target.value;
    renderSavedLeaderboard();
  });
  $("#exportCsvButton").addEventListener("click", handleExportCsv);
  $("#shareButton").addEventListener("click", handleShare);
}

function applyInitialUrlParams() {
  const params = new URLSearchParams(window.location.search);
  $("#seasonInput").max = String(MAX_TRANSLATION_YEAR);
  if (window.location.protocol.startsWith("http")) {
    $("#apiBaseInput").value = window.location.origin;
  }
  if (params.has("player_id")) {
    $("#playerIdInput").value = params.get("player_id");
  }
  if (params.has("year")) {
    $("#seasonInput").value = params.get("year");
    validSeason();
  }
  if (params.has("source_teams")) {
    $("#sourceTeamsInput").value = params.get("source_teams");
  }
  if (params.has("cat")) {
    setSelectedCat(params.get("cat"));
  } else {
    setSelectedCat(DEFAULT_CAT);
  }
  if (params.has("player_type")) {
    setSelectedPlayerType(params.get("player_type"), {resetSelection: false});
  } else {
    setSelectedPlayerType(DEFAULT_PLAYER_TYPE, {resetSelection: false});
  }
}

function shouldDefaultToApiMode() {
  return window.location.protocol.startsWith("http");
}

applyInitialUrlParams();
populateTargetParkSelect();
bindEvents();
if (shouldDefaultToApiMode()) {
  setMode("api");
}
setView("full");
render(state.data);
loadParkProfiles();
renderQueue();
renderHistory();
renderSavedLeaderboard();
renderComparison();
renderSeasonLeaders();
renderPanelStates();
