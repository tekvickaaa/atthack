<script setup lang="ts">

interface MeetingProps {
  meetingId: string;
  meetingTitle: string;
  meetingDescription: string;
  meetingDetails: string[];
  buttonAction: "Intro" | "Outro" | "Sum";
}

const meetings: MeetingProps[] = [
  {
    meetingId: "m1",
    meetingTitle: "Úvodná porada",
    meetingDescription: "Diskusia o pláne projektu.",
    meetingDetails: ["Ciele", "Časová os", "Členovia tímu"],
    buttonAction: "Intro"
  },
  {
    meetingId: "m2",
    meetingTitle: "Technický workshop",
    meetingDescription: "Prezentácia architektúry systému.",
    meetingDetails: ["API", "Databáza", "Backend"],
    buttonAction: "Sum"
  },
  {
    meetingId: "m3",
    meetingTitle: "Marketing meeting",
    meetingDescription: "Plánovanie kampane.",
    meetingDetails: ["Kanály", "Rozpočet", "Cieľová skupina"],
    buttonAction: "Outro"
  },
  {
    meetingId: "m4",
    meetingTitle: "Sprint planning",
    meetingDescription: "Rozdelenie úloh na sprint.",
    meetingDetails: ["Story points", "Tasks", "Priority"],
    buttonAction: "Intro"
  },
  {
    meetingId: "m5",
    meetingTitle: "Retrospektíva",
    meetingDescription: "Zhodnotenie predošlého sprintu.",
    meetingDetails: ["Čo šlo dobre", "Čo zlepšiť", "Action items"],
    buttonAction: "Sum"
  }
];

</script>

<template>
  <UContainer>
    <div class="px-48 pt-6 flex flex-col gap-5">
      <h1 class="text-3xl font-bold ">
        Meetings Page
      </h1>
      <div class="rounded-2xl border border-gray-200 pt-5 h-full overflow-hidden flex flex-col gap-5">
        <MeetingCard
          v-for="meeting in meetings"
          :key="meeting.meetingId"
          :meetingId="meeting.meetingId"
          :meetingTitle="meeting.meetingTitle"
          :meetingDescription="meeting.meetingDescription"
          :meetingDetails="meeting.meetingDetails"
          :buttonAction="meeting.buttonAction"
        />
      </div>
    </div>
  </UContainer>
</template>