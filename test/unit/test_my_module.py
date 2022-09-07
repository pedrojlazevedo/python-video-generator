from python_video_generator.orchestrator import UIForm


def test_main():
    ui = UIForm()
    ui.set_main_window()
    assert 'testing', ui.generate_video()
