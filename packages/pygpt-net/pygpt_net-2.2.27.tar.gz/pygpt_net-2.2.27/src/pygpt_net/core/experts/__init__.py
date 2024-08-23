#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.08.22 00:00:00                  #
# ================================================== #

from pygpt_net.core.bridge import BridgeContext
from pygpt_net.core.dispatcher import Event
from pygpt_net.item.ctx import CtxItem
from pygpt_net.item.preset import PresetItem


class Experts:
    def __init__(self, window=None):
        """
        Experts core

        :param window: Window instance
        """
        self.window = window
        self.allowed_modes = ["chat", "completion", "vision", "langchain", "llama_index"]
        self.allowed_cmds = ["expert_call"]

    def get_mode(self) -> str:
        """
        Get sub-mode to use internally

        :return: sub-mode
        """
        mode = "chat"
        current = self.window.core.config.get("experts.mode")
        if current is not None and current in self.allowed_modes:
            mode = current
        return mode

    def stopped(self) -> bool:
        """
        Check if experts are stopped

        :return: True if stopped
        """
        return self.window.controller.agent.experts.stopped()

    def agent_enabled(self) -> bool:
        """
        Check if agent is enabled

        :return: True if enabled
        """
        return self.window.controller.agent.enabled()

    def get_expert(self, id: str) -> PresetItem:
        """
        Get expert by id

        :param id: expert id
        :return: expert item (preset)
        """
        return self.window.core.presets.get_by_id("expert", id)

    def get_experts(self) -> dict:
        """
        Get experts names with keys

        :return: experts dict
        """
        experts = {}
        presets = self.window.core.presets.get_by_mode("expert")

        # mode: agent
        if self.agent_enabled():
            agents = self.window.core.presets.get_by_mode("agent")
            agent = self.window.core.config.get('preset')
            if agent is not None:
                if agent in agents:
                    for uuid in agents[agent].experts:
                        expert = self.window.core.presets.get_by_uuid(uuid)
                        if expert is not None:
                            id = expert.filename
                            experts[id] = expert.name
        # mode: expert
        else:
            for k in presets:
                if k.startswith("current."):  # skip current
                    continue
                if not presets[k].enabled:  # skip disabled experts
                    continue
                experts[k] = presets[k].name
        return experts

    def get_prompt(self) -> str:
        """
        Get prompt for handle experts

        :return: prompt with list of experts appended
        """
        prompt = self.window.core.config.get('prompt.expert')
        if self.window.core.command.is_native_enabled():
            prompt = """
            EXPERT MODE IS ENABLED
            ======================
            You are the professional manager of a team of experts, each of whom is the best in their respective fields. 
            
            IMPORTANT RULES:
            
            YOU MUST ALWAYS FOLLOW THIS RULES WHILE MANAGING EXPERTS:
            
            1. Instead of directly answering questions, you can manage these experts by forwarding queries to them, 
            collecting their responses, and controlling the flow of information between them as well as sending 
            requests to them. 
            2. You will serve as a bridge between them. 
            3. Each expert has their own conversation context, so you can communicate with them normally. 
            4. The experts can communicate with you but not with each other, so you will be responsible for relaying 
            information between them. 
            5. After consulting with the experts, your task will be to prepare the best possible answer based on the 
            assistance received and to use it in your Chain-of-Thought. 
            6. To send a request to an expert prepare the "expert_call" function call.
            7. Remember that the call must contain a query and the ID of the expert to be forwarded to the expert. 
            8. Use ONLY experts listed below, DO NOT TRY to ask any non-existing experts - they will not respond.
            9. Do not respond to the expert's replies, or use commands again if replying; the expert only has 
            the ability to listen to your queries sent and to respond to them.
            10. Always follow ALL user commands, even if you thing than expert can't do something. 
            Experts are allowed to execute commands same as you can.
            11. After query an expert, always wait for expert response before sending another query.
            12. Do not try to query experts in the middle of the conversation, put your queries and commands at the end of the text.
            13. Always call only one expert at a time.
            14. Always execute only one function call at a time.
            15. Always use the language used by user in conversation.
            16. Never write as an called expert and do not imagine response from him.
            17. Your response cannot include ~###~{...}~###~ commands in the conversation body - this syntax is reserved only for response purposes.
            18. First message after your query is always a response from asked expert, not from me.
            
            List of available experts, along with their IDs:
            
            {presets}
            """
        experts = self.get_experts()
        experts_list = []
        for k in experts:
            if k.startswith("current."): # skip current presets
                continue
            experts_list.append(" - " + str(k) + ": " + str(experts[k]))
        prompt = prompt.replace("{presets}", "\n".join(experts_list))
        return prompt

    def extract_calls(self, ctx: CtxItem) -> dict:
        """
        Extract expert calls from context output

        :param ctx: context item
        :return: dict with calls
        """
        ids = self.get_experts().keys()
        if not ids:  # abort if no experts
            return {}
        cmds = self.window.core.command.extract_cmds(ctx.output)
        if len(cmds) > 0:
            ctx.cmds = cmds  # append commands to ctx
        else:  # abort if no cmds
            return {}
        commands = self.window.core.command.from_commands(cmds)  # pack to execution list
        is_cmd = False
        my_commands = []
        calls = {}
        for item in commands:
            if item["cmd"] in self.allowed_cmds:
                my_commands.append(item)
                is_cmd = True
        if not is_cmd:  # abort if no expert calls
            return {}
        for item in my_commands:
            try:
                if item["cmd"] == "expert_call":
                    if "params" not in item:
                        continue
                    if "id" not in item["params"] or "query" not in item["params"]:
                        continue
                    id = item["params"]["id"]
                    if id not in ids:
                        continue
                    query = item["params"]["query"]
                    calls[id] = query
            except Exception as e:
                self.window.core.debug.error(e)
                return {}
        return calls

    def reply(self, ctx: CtxItem):
        """
        Re-send response from commands to master expert

        :param ctx: context item
        """
        if self.stopped():
            return

        internal = False
        if self.agent_enabled():  # hide in agent mode
            internal = True
        if ctx.output.strip() != "":
            response = ctx.output
        else:
            response = ctx.input
        self.window.controller.chat.input.send(
            "Result from expert:\n\n" + str(response),
            force=True,
            reply=True,
            internal=internal,
            prev_ctx=ctx,
        )

    def call(
            self,
            master_ctx: CtxItem,
            expert_id: str,
            query: str
    ):
        """
        Call the expert

        :param master_ctx: master context
        :param expert_id: expert id (preset ID)
        :param query: input text (master prompt)
        """
        if self.stopped():
            return

        # get or create children meta
        slave = self.window.core.ctx.get_or_create_slave_meta(master_ctx, expert_id)
        expert = self.get_expert(expert_id)
        reply = True
        hidden = False
        internal = False

        if self.agent_enabled():  # hide in agent mode
            internal = False
            hidden = True

        mode = self.get_mode()
        base_mode = mode
        model = expert.model
        user_name = expert.name
        ai_name = expert.name
        sys_prompt = expert.prompt
        model_data = self.window.core.models.get(model)

        files = []
        file_ids = []
        functions = []
        tools_outputs = []

        # from current config
        max_tokens = self.window.core.config.get('max_output_tokens')
        stream_mode = self.window.core.config.get('stream')

        # create slave item
        ctx = CtxItem()
        ctx.meta_id = slave.id
        ctx.internal = internal
        ctx.hidden = hidden
        ctx.current = True  # mark as current context item
        ctx.mode = mode  # store current selected mode (not inline changed)
        ctx.model = model  # store model list key, not real model id
        ctx.set_input(query, user_name)
        ctx.set_output(None, str(ai_name))
        ctx.sub_call = True  # mark as sub-call

        # render: begin
        self.window.controller.chat.render.begin(stream=stream_mode)
        self.window.core.ctx.provider.append_item(slave, ctx)  # to slave meta

        # build sys prompt
        sys_prompt_raw = sys_prompt  # store raw prompt
        event = Event(Event.PRE_PROMPT, {
            'mode': mode,
            'value': sys_prompt,
        })
        self.window.core.dispatcher.dispatch(event)
        sys_prompt = event.data['value']
        sys_prompt = self.window.core.prompt.prepare_sys_prompt(
            mode,
            sys_prompt,
            ctx,
            reply,
            internal,
        )

        # call bridge
        history = self.window.core.ctx.all(
            meta_id=slave.id
        )  # get history for slave ctx
        bridge_context = BridgeContext(
            ctx=ctx,
            history=history,
            mode=mode,
            parent_mode=base_mode,
            model=model_data,
            system_prompt=sys_prompt,
            system_prompt_raw=sys_prompt_raw,
            prompt=query,
            stream=stream_mode,
            attachments=files,
            file_ids=file_ids,
            assistant_id=self.window.core.config.get('assistant'),
            idx=self.window.controller.idx.current_idx,
            idx_raw=self.window.core.config.get('llama.idx.raw'),
            external_functions=functions,
            tools_outputs=tools_outputs,
            max_tokens=max_tokens,
        )
        self.window.controller.chat.common.lock_input()  # lock input
        result = self.window.core.bridge.call(
            context=bridge_context,
        )
        if not result:  # abort if bridge call failed
            return

        # handle output
        ctx.current = False  # reset current state
        self.window.core.ctx.update_item(ctx)
        ctx.from_previous()  # append previous result if exists
        self.window.controller.chat.output.handle(
            ctx,
            mode,
            stream_mode,
        )
        ctx.clear_reply()  # reset results
        self.window.controller.chat.output.handle_cmd(ctx)  # handle cmds
        ctx.from_previous()  # append previous result again before save
        self.window.core.ctx.update_item(ctx)  # update ctx in DB

        # if commands reply after bridge call, then stop (already handled in dispatcher)
        if ctx.reply:
            return

        # send slave expert response to master expert
        self.window.controller.chat.input.send(
            "@"+expert_id+" says:\n\n" + str(ctx.output),
            force=True,
            reply=False,
            internal=False,
            prev_ctx=ctx,
        )

    def get_functions(self) -> list:
        """
        Append goal commands

        :return: goal commands
        """
        cmds = [
            {
                "cmd": "expert_call",
                "instruction": "Call an expert",
                "params": [
                    {
                        "name": "id",
                        "description": "expert id",
                        "required": True,
                        "type": "str",
                    },
                    {
                        "name": "query",
                        "description": "query to expert",
                        "required": False,
                        "type": "str",
                    }
                ]
            }
        ]
        return cmds
