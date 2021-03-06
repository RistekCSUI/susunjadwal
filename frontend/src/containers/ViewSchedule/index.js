import { CopyToClipboard } from "react-copy-to-clipboard";
import { useSelector, useDispatch } from "react-redux";
import React, { useEffect, useState } from "react";
import { useParams } from 'react-router';
import { Link } from 'react-router-dom';
import styled from "styled-components";
import Helmet from "react-helmet";

import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent as ChakraModalContent,
  ModalFooter as ChakraModalFooter,
  ModalBody,
  useDisclosure
} from "@chakra-ui/react"

import { getSchedule, postRenameSchedule, deleteSchedule } from "services/api";
import { makeAtLeastMs } from "utils/promise";
import { setLoading } from "redux/modules/appState";
import Schedule from "./Schedule";
import ControlledInput from "./ControlledInput";
import { decodeHtmlEntity } from "utils/string";

import deleteImg from "assets/Delete.svg";
import clipboardImg from "assets/Clipboard.svg";
import { SuccessToast } from "components/Toast";

function ViewSchedule({ match, history }) {
  const isMobile = useSelector(state => state.appState.isMobile);
  const { isOpen, onOpen, onClose } = useDisclosure()
  const auth = useSelector(state => state.auth);
  const { scheduleId } = useParams();
  const dispatch = useDispatch();

  const [schedule, setSchedule] = useState(null);
  const [createdAt, setCreatedAt] = useState(null);

  async function onRename(slug, value) {
    if (auth) {
      await postRenameSchedule(auth.userId, slug, value);
      setSchedule({ ...schedule, name: value });
    };
  };

  useEffect(() => {
    async function fetchSchedule() {
      dispatch(setLoading(true));
      const {
        data: { user_schedule }
      } = await makeAtLeastMs(getSchedule(match.params.scheduleId), 1000);
      setSchedule(user_schedule);
      setCreatedAt(new Date(user_schedule.created_at))
      dispatch(setLoading(false));
    }
    fetchSchedule();
  }, [match, dispatch]);

  const scheduleName = schedule && schedule.name;

  const showAlertCopy = () => {
    SuccessToast(
      "Link telah disalin! Kamu bisa bagikan link tersebut ke teman kamu.",
      isMobile
    );
  }

  const performDeleteSchedule = async (userId, scheduleId) => {
    dispatch(setLoading(true));
    await makeAtLeastMs(deleteSchedule(userId, scheduleId), 1000);
    history.push('/jadwal');
  }

  const confirmDeleteSchedule = (scheduleId) => {
      performDeleteSchedule(auth.userId, scheduleId);
  }

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalBody>
            Apakah kamu yakin ingin menghapus jadwal?
          </ModalBody>

          <ModalFooter>
            <Button
              onClick={onClose}
              variant="outline"
            >
              Batal
            </Button>
            <Button
              onClick={() => confirmDeleteSchedule(schedule.id)}
              variant="danger"
            >
              Hapus
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      <MainContainer>
        <Helmet
          title={scheduleName ? `Jadwal ${scheduleName}` : `Jadwal Untitled`}
          meta={[{ name: "description", content: "Description of Jadwal" }]}
        />

        {schedule && (
          <Container>
            <HeaderContainer>
              {schedule.has_edit_access ? (
                <ScheduleNameEditable>
                  <ControlledInput
                    name={decodeHtmlEntity(schedule.name)}
                    slug={match.params.scheduleId}
                    rename={onRename}
                  />
                  <p>
                    Dibuat pada {" "}
                    {createdAt?.getDate() + "/"
                    + (createdAt?.getMonth() + 1) + "/"
                    + createdAt?.getFullYear()}
                  </p>
                </ScheduleNameEditable>
              ) : (
                  <ScheduleName>
                    {decodeHtmlEntity(schedule.name)}
                  </ScheduleName>
                )}
                <ButtonContainer>
                  <ImageButton
                    onClick={onOpen}
                  >
                    <img src={deleteImg} alt="delete"/>
                  </ImageButton>
                  <CopyToClipboard
                    text={`${window.location.href}/${schedule.id}`}
                    onCopy={showAlertCopy}
                  >
                    <ImageButton>
                      <img src={clipboardImg} alt="copy"/>
                    </ImageButton>
                  </CopyToClipboard>
                </ButtonContainer>
            </HeaderContainer>

            <Link to={`/edit/${scheduleId}`} >
              <Button
                intent="primary"
                variant="outline"
                onClick={() => null}
                mt={{ base: "24px", lg: "0px" }}
              >
                {schedule.has_edit_access ? 'Edit' : 'Copy'}
              </Button>
            </Link>
          </Container>
        )}

        <Schedule
          width="100%"
          pxPerMinute={isMobile ? 0.7 : 0.9}
          schedule={schedule}
          startHour={7}
          endHour={21}
          showHeader
          showLabel
          showRoom
        />
      </MainContainer>
    </>
  );
}

const ModalContent = styled(ChakraModalContent).attrs({
  padding: { base: "16px 24px", lg: "20px 24px" },
  width: { base: "90%", lg: "initial" },
  textAlign: "center"
})``;

const ModalFooter = styled(ChakraModalFooter).attrs({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginTop: { base: "12px", lg: "16px" }
})`
  button {
    margin: 0px 4px;
  }
`;

const MainContainer = styled.div`
  padding: 0px !important;
  margin: -56px -24px 0;

  @media (min-width: 900px) {
    margin: -36px -80px 0;
  }
`;

const Container = styled.div`
  padding: 32px 24px 20px;

  @media (min-width: 900px) {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 32px 80px 20px;

    & > :nth-child(1) {
      flex-grow: 1;
    }
  }
`;

const HeaderContainer = styled.div`
  display: flex;
  align-items: center;
  background-color: transparent;
  justify-content: space-between;
  margin-right: -16px;

  @media (min-width: 900px) {
    margin-right: 0px;
  }
`;

const ScheduleNameEditable = styled.div`
  p {
    text-align: left;
    margin-top: 4px;
    font-size: 12px;
  }

  @media (min-width: 900px) {
    p {
      font-size: 14px;
    }
  }
`;

const ScheduleName = styled.div`
  font-size: 32px;
  color: white;
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-direction: row;
`;

const ImageButton = styled.div`
  justify-content: center;
  margin-right: 1rem;
  cursor: pointer;
  display: flex;
`;

export default ViewSchedule;
