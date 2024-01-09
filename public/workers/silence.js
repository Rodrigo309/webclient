onmessage = async (e) => {
  const { ending_file, starting_file } = e.data;

  const is_dev = location.port === "5173";
  const base_url = is_dev ? "http://localhost:1980" : location.origin;
  const url = base_url + "/file/silence";

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ end: ending_file, start: starting_file }),
  });

  const data = await res.json();
  postMessage(data);
};
