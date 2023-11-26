const GPTResearcher = (() => {
  const init = () => {
    // Not sure, but I think it would be better to add event handlers here instead of in the HTML
    //document.getElementById("startResearch").addEventListener("click", startResearch);
  }

  const startResearch = () => {
    document.getElementById("output").innerHTML = "";

    addAgentResponse({ output: "🤔 Thinking about research questions for the task..." });

    listenToSockEvents();
  };

  const listenToSockEvents = () => {
    const { protocol, host, pathname } = window.location;
    const ws_uri = `${protocol === 'https:' ? 'wss:' : 'ws:'}//${host}${pathname}ws`;
    const socket = new WebSocket(ws_uri);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'logs') {
        addAgentResponse(data);
      } else if (data.type === 'path') {
        updateDownloadLink(data);

      }
    };

    socket.onopen = (event) => {
      const blog = document.querySelector('input[name="blog"]').value;
      const purpose = document.querySelector('select[name="purpose"]').value;
      const targetAudience = document.querySelector('select[name="target audience"]').value;
      const platform = document.querySelector('select[name="platform"]').value;
      console.log(blog);

      const requestData = {
        blog: blog,
        purpose: purpose,
        target_audience: targetAudience,
        platform: platform
      };

      socket.send(`start ${JSON.stringify(requestData)}`);
    };
  };

  const addAgentResponse = (data) => {
    const output = document.getElementById("output");
    output.innerHTML += '<div class="agent_response">' + data.output + '</div>';
    output.scrollTop = output.scrollHeight;
    output.style.display = "block";
    updateScroll();
  };

  const updateDownloadLink = (data) => {
    const path = data.output;
    document.getElementById("downloadLink").setAttribute("href", path);
  };

  const updateScroll = () => {
    window.scrollTo(0, document.body.scrollHeight);
  };

  document.addEventListener("DOMContentLoaded", init);
  return {
    startResearch,
  };
})();