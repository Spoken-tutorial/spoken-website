import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { AuthService } from 'src/app/_service/auth.service';

@Component({
  selector: 'app-script-comment-box',
  templateUrl: './script-comment-box.component.html',
  styleUrls: ['./script-comment-box.component.sass']
})
export class ScriptCommentBoxComponent implements OnInit {
  @Input() comment: any;
  @Input() index: number;
  @Input() published: boolean = false;
  @Output() saveCommentEmitter = new EventEmitter<number>();
  @Output() deleteCommentEmitter = new EventEmitter<number>();
  @Output() doneCommentEmitter = new EventEmitter<number>();
  @Output() resolveCommentEmitter = new EventEmitter<number>();

  isEditable: boolean = false;

  constructor(
    public authService: AuthService
  ) { }

  makeEditable() {
    this.isEditable = true;
  }

  saveComment() {
    this.saveCommentEmitter.emit(this.index);
    this.isEditable = false;
  }

  deleteComment() {
    this.deleteCommentEmitter.emit(this.index);
  }

  doneComment() {
    this.doneCommentEmitter.emit(this.index);
  }

  resolveComment() {
    this.resolveCommentEmitter.emit(this.index);
  }

  ngOnInit() {
  }

}
