import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-script-comment',
  templateUrl: './script-comment.component.html',
  styleUrls: ['./script-comment.component.sass']
})
export class ScriptCommentComponent implements OnInit {
  @Input() newComment: string;
  @Input() comments: any;
  @Output() commentEmitter = new EventEmitter<string>();

  constructor() { }

  public addComment() {
    // console.log(this.newComment)
    this.commentEmitter.emit(this.newComment);
  }

  commentKey(event) { this.newComment = event.target.value; }

  ngOnInit() {

  }

}
